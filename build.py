from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CONTENT_PATH = ROOT / "resume.md"
POSTS_DIR = ROOT / "posts"
FEATURED_PATH = ROOT / "featured.md"
STATIC_DIR = ROOT / "static"
DIST_DIR = ROOT / "site"
ASSET_FILES = ("product.jpeg",)
ASSET_DIRS = ("icon", "media")
PDF_FILENAME = "resume.pdf"
LATEST_POSTS_COUNT = 3

NAV_ITEMS = (
    ("index.html", "Home", "home"),
    ("publications.html", "Publications", "publications"),
    ("blog.html", "Blog", "blog"),
)
PUBLICATION_SECTIONS = (
    "International Publications & Conferences",
    "Domestic Conferences",
)


@dataclass
class Page:
    title: str
    body: str
    sidebar: str


@dataclass
class Post:
    slug: str
    title: str
    date: str
    summary: str
    lang: str
    body: str


@dataclass
class Featured:
    title: str
    match: str = ""
    image: str = ""
    venue: str = ""
    blurb: str = ""
    citation: str = ""
    links: list[tuple[str, str]] = field(default_factory=list)


def print_url(url: str) -> str:
    if url.startswith("mailto:"):
        return url.removeprefix("mailto:")
    return url


def render_inline(text: str) -> str:
    escaped = html.escape(text, quote=True)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = escaped.replace('K. Ikeda', '<span class="highlight-name">K. Ikeda</span>')

    def link(match: re.Match[str]) -> str:
        label = match.group(1)
        raw_url = match.group(2)
        url = html.escape(raw_url, quote=True)
        visible_url = html.escape(print_url(raw_url), quote=True)
        return f'<a href="{url}" data-print-url="{visible_url}">{label}</a>'

    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, escaped)


def render_image(alt: str, src: str) -> str:
    alt_attr = html.escape(alt, quote=True)
    src_attr = html.escape(src, quote=True)
    return f'<img class="profile-icon" src="{src_attr}" alt="{alt_attr}">'


def render_contact_links(text: str) -> str:
    icon_map = {
        "Email": "icon/email.png",
        "Google Scholar": "icon/google-sholar.png",
        "GitHub": "icon/github.png",
        "LinkedIn": "icon/linkdin.png",
        "X": "icon/x.png",
    }
    links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", text)
    items = []
    for label, url in links:
        label_attr = html.escape(label, quote=True)
        url_attr = html.escape(url, quote=True)
        visible_url_attr = html.escape(print_url(url), quote=True)
        icon_src = html.escape(icon_map.get(label, ""), quote=True)
        if icon_src:
            icon_html = f'<img src="{icon_src}" alt="" aria-hidden="true">'
        else:
            icon_html = f"<span>{html.escape(label[:2], quote=True)}</span>"
        items.append(
            f'<a class="contact-link" href="{url_attr}" title="{label_attr}" '
            f'aria-label="{label_attr}" data-print-url="{visible_url_attr}">'
            f'{icon_html}<span class="contact-label">{label_attr}</span></a>'
        )
    if not items:
        return f"<p>{render_inline(text)}</p>"
    return '<nav class="contact-icons" aria-label="Contact links">' + "".join(items) + "</nav>"


def render_pdf_export_link() -> str:
    return (
        f'<a class="contact-link pdf-export-link" href="{PDF_FILENAME}" '
        'aria-label="Download resume as PDF">'
        '<span class="pdf-badge" aria-hidden="true">CV</span>'
        '<span class="contact-label">resume (PDF)</span>'
        "</a>"
    )


def render_body(source: str) -> str:
    """Render general-purpose Markdown (blog posts) to HTML using only stdlib."""
    blocks: list[str] = []
    paragraph: list[str] = []
    ul_items: list[str] = []
    ol_items: list[str] = []
    in_code = False
    code_lines: list[str] = []
    code_lang = ""

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            blocks.append(f"<p>{render_inline(' '.join(paragraph))}</p>")
            paragraph = []

    def flush_ul() -> None:
        nonlocal ul_items
        if ul_items:
            blocks.append("<ul>" + "".join(f"<li>{item}</li>" for item in ul_items) + "</ul>")
            ul_items = []

    def flush_ol() -> None:
        nonlocal ol_items
        if ol_items:
            blocks.append("<ol>" + "".join(f"<li>{item}</li>" for item in ol_items) + "</ol>")
            ol_items = []

    def flush_all() -> None:
        flush_paragraph()
        flush_ul()
        flush_ol()

    for raw_line in source.splitlines():
        fence = re.match(r"^\s*```(.*)$", raw_line)
        if in_code:
            if fence:
                code = "\n".join(code_lines)
                cls = f' class="language-{html.escape(code_lang, quote=True)}"' if code_lang else ""
                blocks.append(f"<pre><code{cls}>{html.escape(code)}</code></pre>")
                in_code = False
                code_lines = []
                code_lang = ""
            else:
                code_lines.append(raw_line)
            continue
        if fence:
            flush_all()
            in_code = True
            code_lang = fence.group(1).strip()
            continue

        line = raw_line.strip()

        if not line:
            flush_all()
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            flush_all()
            level = len(heading.group(1))
            blocks.append(f"<h{level}>{render_inline(heading.group(2).strip())}</h{level}>")
            continue

        image = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", line)
        if image:
            flush_all()
            alt = html.escape(image.group(1).strip(), quote=True)
            src = html.escape(image.group(2).strip(), quote=True)
            caption = f"<figcaption>{alt}</figcaption>" if alt else ""
            blocks.append(
                f'<figure class="post-figure"><img src="{src}" alt="{alt}">{caption}</figure>'
            )
            continue

        quote = re.match(r"^>\s?(.*)$", line)
        if quote:
            flush_all()
            blocks.append(f"<blockquote><p>{render_inline(quote.group(1).strip())}</p></blockquote>")
            continue

        ordered = re.match(r"^\d+\.\s+(.+)$", line)
        if ordered:
            flush_paragraph()
            flush_ul()
            ol_items.append(render_inline(ordered.group(1).strip()))
            continue

        bullet = re.match(r"^[-*+]\s+(.+)$", line)
        if bullet:
            flush_paragraph()
            flush_ol()
            ul_items.append(render_inline(bullet.group(1).strip()))
            continue

        paragraph.append(line)

    flush_all()
    return "\n".join(blocks)


def render_markdown(source: str) -> Page:
    title = "Resume"
    blocks: list[str] = []
    sidebar_blocks: list[str] = []
    paragraph: list[str] = []
    list_items: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            blocks.append(f"<p>{render_inline(' '.join(paragraph))}</p>")
            paragraph = []

    def flush_list() -> None:
        nonlocal list_items
        if list_items:
            blocks.append("<ul>" + "".join(f"<li>{item}</li>" for item in list_items) + "</ul>")
            list_items = []

    for raw_line in source.splitlines():
        line = raw_line.strip()

        if not line:
            flush_paragraph()
            flush_list()
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            flush_paragraph()
            flush_list()
            level = len(heading.group(1))
            text = heading.group(2).strip()
            if level == 1 and title == "Resume":
                title = re.sub(r"\s+", " ", text)
            blocks.append(f"<h{level}>{render_inline(text)}</h{level}>")
            continue

        image = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", line)
        if image:
            flush_paragraph()
            flush_list()
            sidebar_blocks.append(render_image(image.group(1).strip(), image.group(2).strip()))
            continue

        if line.startswith("Contact:"):
            flush_paragraph()
            flush_list()
            sidebar_blocks.append(render_contact_links(line))
            continue

        if line.startswith("Affiliation:") or line.startswith("Location:"):
            flush_paragraph()
            flush_list()
            _, value = line.split(":", 1)
            sidebar_blocks.append(f'<p class="sidebar-meta">{render_inline(value.strip())}</p>')
            continue

        bullet = re.match(r"^[-*+]\s+(.+)$", line)
        if bullet:
            flush_paragraph()
            list_items.append(render_inline(bullet.group(1).strip()))
            continue

        paragraph.append(line)

    flush_paragraph()
    flush_list()
    return Page(title=title, body="\n".join(blocks), sidebar="\n".join(sidebar_blocks))


def render_nav(active: str) -> str:
    links = []
    for href, label, key in NAV_ITEMS:
        current = ' aria-current="page"' if key == active else ""
        links.append(f'<a href="{href}"{current}>{html.escape(label)}</a>')
    return (
        '<header class="site-nav"><div class="site-nav-inner">'
        '<a class="site-brand" href="index.html">K. Ikeda</a>'
        '<nav aria-label="Primary navigation">' + "".join(links) + "</nav>"
        "</div></header>"
    )


def html_document(title: str, active: str, body_html: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
{render_nav(active)}
{body_html}
</body>
</html>
"""


def format_date(value: str) -> str:
    match = re.match(r"^(\d{4})-(\d{2})-(\d{2})", value.strip())
    if not match:
        return value.strip()
    months = (
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    )
    year, month, day = match.groups()
    idx = int(month) - 1
    if 0 <= idx < 12:
        return f"{months[idx]} {int(day)}, {year}"
    return value.strip()


def render_post_list(posts: list[Post]) -> str:
    if not posts:
        return '<p class="empty-note">No posts yet. Check back soon.</p>'
    items = []
    for post in posts:
        meta = format_date(post.date)
        meta_html = f'<p class="post-meta"><time>{html.escape(meta)}</time></p>' if meta else ""
        summary_html = (
            f'<p class="post-summary">{render_inline(post.summary)}</p>' if post.summary else ""
        )
        items.append(
            '<li class="post-list-item">'
            f'<h3><a href="{html.escape(post.slug, quote=True)}.html">'
            f"{render_inline(post.title)}</a></h3>"
            f"{meta_html}{summary_html}"
            "</li>"
        )
    return '<ul class="post-list">' + "".join(items) + "</ul>"


def render_latest_posts(posts: list[Post]) -> str:
    if not posts:
        return ""
    return (
        '<section class="latest-posts" aria-label="Latest posts">'
        '<div class="latest-posts-head"><h2>Latest posts</h2>'
        '<a class="all-posts-link" href="blog.html">All posts &rarr;</a></div>'
        f"{render_post_list(posts)}"
        "</section>"
    )


def render_home(resume_page: Page, latest_posts: list[Post]) -> str:
    body = f"""  <div class="layout">
    <div class="page-actions">
      {render_pdf_export_link()}
    </div>
    <aside class="sidebar">
{resume_page.sidebar}
    </aside>
    <main class="page">
{resume_page.body}
{render_latest_posts(latest_posts)}
    </main>
  </div>"""
    return html_document(resume_page.title, "home", body)


def render_blog_index(posts: list[Post]) -> str:
    body = (
        '  <main class="content">\n'
        "    <h1>Blog</h1>\n"
        '    <p class="lead">Notes on LiDAR sensing, autonomous driving perception, and sensor security.</p>\n'
        f"    {render_post_list(posts)}\n"
        "  </main>"
    )
    return html_document("Blog", "blog", body)


def render_post_page(post: Post) -> str:
    meta = format_date(post.date)
    meta_html = f'<p class="post-meta"><time>{html.escape(meta)}</time></p>' if meta else ""
    body = (
        '  <main class="content post">\n'
        '    <p class="back-link"><a href="blog.html">&larr; Blog</a></p>\n'
        f"    <h1>{render_inline(post.title)}</h1>\n"
        f"    {meta_html}\n"
        f"    <div class=\"post-body\">\n{post.body}\n    </div>\n"
        "  </main>"
    )
    return html_document(post.title, "blog", body)


def render_pub_card(card: Featured) -> str:
    media = ""
    if card.image:
        media = (
            '<div class="pub-card-media">'
            f'<img src="{html.escape(card.image, quote=True)}" '
            f'alt="{html.escape(card.title, quote=True)}"></div>'
        )
    venue = f'<p class="pub-venue">{render_inline(card.venue)}</p>' if card.venue else ""
    blurb = f'<p class="pub-blurb">{render_inline(card.blurb)}</p>' if card.blurb else ""
    citation = (
        f'<p class="pub-citation">{render_inline(card.citation)}</p>' if card.citation else ""
    )
    links = ""
    if card.links:
        buttons = "".join(
            f'<a class="pub-link" href="{html.escape(url, quote=True)}">{html.escape(label)}</a>'
            for label, url in card.links
        )
        links = f'<div class="pub-links">{buttons}</div>'
    card_class = "pub-card" if card.image else "pub-card pub-card--text"
    return (
        f'<article class="{card_class}">'
        f"{media}"
        '<div class="pub-card-body">'
        f"<h3>{render_inline(card.title)}</h3>"
        f"{venue}{blurb}{citation}{links}"
        "</div></article>"
    )


def render_publications(featured: list[Featured], by_year: dict[str, list[str]]) -> str:
    sections = ['  <main class="content">', "    <h1>Publications</h1>"]
    sections.append(
        '    <p class="lead">Selected and full list of publications. '
        "Asterisks (*) denote equal contribution.</p>"
    )

    if featured:
        cards = "".join(render_pub_card(card) for card in featured)
        sections.append('    <section class="pub-featured" aria-label="Featured publications">')
        sections.append("      <h2>Featured</h2>")
        sections.append(f'      <div class="pub-card-grid">{cards}</div>')
        sections.append("    </section>")

    sections.append('    <section class="pub-all" aria-label="All publications">')
    sections.append("      <h2>All publications</h2>")
    if by_year:
        for year in sort_years(by_year.keys()):
            items = "".join(f"<li>{render_inline(text)}</li>" for text in by_year[year])
            sections.append(f'      <h3 class="pub-year">{html.escape(year)}</h3>')
            sections.append(f'      <ul class="pub-year-list">{items}</ul>')
    else:
        sections.append('      <p class="empty-note">No publications found.</p>')
    sections.append("    </section>")
    sections.append("  </main>")
    return html_document("Publications", "publications", "\n".join(sections))


def split_frontmatter(source: str) -> tuple[dict[str, str], str]:
    lines = source.splitlines()
    if lines and lines[0].strip() == "---":
        meta: dict[str, str] = {}
        index = 1
        while index < len(lines) and lines[index].strip() != "---":
            line = lines[index]
            if ":" in line:
                key, value = line.split(":", 1)
                meta[key.strip().lower()] = value.strip()
            index += 1
        body = "\n".join(lines[index + 1 :])
        return meta, body
    return {}, source


def load_posts() -> list[Post]:
    posts: list[Post] = []
    if not POSTS_DIR.exists():
        return posts
    for path in sorted(POSTS_DIR.glob("*.md")):
        if path.stem.startswith("_"):
            continue  # drafts/templates: skip files whose name starts with "_"
        meta, body = split_frontmatter(path.read_text(encoding="utf-8"))
        posts.append(
            Post(
                slug=path.stem,
                title=meta.get("title", path.stem),
                date=meta.get("date", ""),
                summary=meta.get("summary", ""),
                lang=meta.get("lang", "en"),
                body=render_body(body),
            )
        )
    posts.sort(key=lambda post: post.date, reverse=True)
    return posts


def extract_year(text: str) -> str:
    years = re.findall(r"\b(19\d{2}|20\d{2})\b", text)
    return years[-1] if years else "Other"


def parse_publications(source: str) -> tuple[list[str], dict[str, list[str]]]:
    entries: list[str] = []
    in_section = False
    for raw_line in source.splitlines():
        line = raw_line.strip()
        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            in_section = heading.group(2).strip() in PUBLICATION_SECTIONS
            continue
        if in_section:
            bullet = re.match(r"^[-*+]\s+(.+)$", line)
            if bullet:
                entries.append(bullet.group(1).strip())
    by_year: dict[str, list[str]] = {}
    for text in entries:
        by_year.setdefault(extract_year(text), []).append(text)
    return entries, by_year


def sort_years(years) -> list[str]:
    numeric = sorted((y for y in years if y.isdigit()), key=int, reverse=True)
    other = [y for y in years if not y.isdigit()]
    return numeric + other


def load_featured() -> list[Featured]:
    if not FEATURED_PATH.exists():
        return []
    items: list[Featured] = []
    current: Featured | None = None
    for raw_line in FEATURED_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        heading = re.match(r"^##\s+(.+)$", line)
        if heading:
            title = heading.group(1).strip()
            current = Featured(title=title, match=title)
            items.append(current)
            continue
        if current is not None and ":" in line:
            key, value = line.split(":", 1)
            field_name = key.strip().lower()
            value = value.strip()
            if field_name == "image":
                current.image = value
            elif field_name == "venue":
                current.venue = value
            elif field_name == "blurb":
                current.blurb = value
            elif field_name == "match":
                current.match = value
            else:
                current.links.append((key.strip(), value))
    return items


def build_featured(featured: list[Featured], entries: list[str]) -> list[Featured]:
    """Attach matching resume citations and drop missing teaser images."""
    resolved: list[Featured] = []
    for card in featured:
        needle = card.match.lower()
        for entry in entries:
            if needle and needle in entry.lower():
                card.citation = entry
                break
        if card.image and not (ROOT / card.image).exists():
            card.image = ""
        resolved.append(card)

    if resolved:
        return resolved

    # Fallback: feature the most recent entries (document order) without images.
    fallback: list[Featured] = []
    for entry in entries[:2]:
        fallback.append(Featured(title=entry, venue=extract_year(entry)))
    return fallback


def render_html(page: Page) -> str:
    """Backwards-compatible single-page resume render (no blog/publications)."""
    return render_home(page, [])


def find_browser() -> Path | None:
    candidates = [
        "msedge",
        "microsoft-edge",
        "microsoft-edge-stable",
        "chrome",
        "chromium",
        "chromium-browser",
        "google-chrome",
        "google-chrome-stable",
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    for candidate in candidates:
        resolved = shutil.which(candidate)
        if resolved:
            return Path(resolved)
        path = Path(candidate)
        if path.exists():
            return path
    return None


def build_pdf(html_path: Path, pdf_path: Path) -> None:
    browser = find_browser()
    if browser is None:
        raise RuntimeError(
            "Could not find Microsoft Edge, Google Chrome, or Chromium to generate the PDF."
        )

    command = [
        str(browser),
        "--headless=new",
        "--no-sandbox",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path.resolve()}",
        html_path.resolve().as_uri(),
    ]
    subprocess.run(command, check=True)


def build() -> None:
    source = CONTENT_PATH.read_text(encoding="utf-8")
    resume_page = render_markdown(source)
    posts = load_posts()
    entries, by_year = parse_publications(source)
    featured = build_featured(load_featured(), entries)

    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True)

    html_path = DIST_DIR / "index.html"
    html_path.write_text(render_home(resume_page, posts[:LATEST_POSTS_COUNT]), encoding="utf-8")
    (DIST_DIR / "publications.html").write_text(
        render_publications(featured, by_year), encoding="utf-8"
    )
    (DIST_DIR / "blog.html").write_text(render_blog_index(posts), encoding="utf-8")
    for post in posts:
        (DIST_DIR / f"{post.slug}.html").write_text(render_post_page(post), encoding="utf-8")

    if STATIC_DIR.exists():
        for path in STATIC_DIR.iterdir():
            if path.is_file():
                shutil.copy2(path, DIST_DIR / path.name)
    for filename in ASSET_FILES:
        path = ROOT / filename
        if path.exists():
            shutil.copy2(path, DIST_DIR / filename)
    for dirname in ASSET_DIRS:
        path = ROOT / dirname
        if path.exists():
            shutil.copytree(path, DIST_DIR / dirname)
    build_pdf(html_path, DIST_DIR / PDF_FILENAME)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the personal site static pages.")
    parser.parse_args()
    build()
    print(f"Built {DIST_DIR / 'index.html'}")
    print(f"Built {DIST_DIR / 'publications.html'}")
    print(f"Built {DIST_DIR / 'blog.html'}")
    print(f"Built {DIST_DIR / PDF_FILENAME}")


if __name__ == "__main__":
    main()
