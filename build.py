from __future__ import annotations

import argparse
import html
import re
import shutil
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CONTENT_PATH = ROOT / "resume.md"
STATIC_DIR = ROOT / "static"
DIST_DIR = ROOT / "site"
ASSET_FILES = ("product.jpeg",)
ASSET_DIRS = ("icon",)


@dataclass
class Page:
    title: str
    body: str
    sidebar: str


def render_inline(text: str) -> str:
    escaped = html.escape(text, quote=True)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = escaped.replace('K. Ikeda', '<span class="highlight-name">K. Ikeda</span>')

    def link(match: re.Match[str]) -> str:
        label = match.group(1)
        url = html.escape(match.group(2), quote=True)
        return f'<a href="{url}">{label}</a>'

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
        icon_src = html.escape(icon_map.get(label, ""), quote=True)
        if icon_src:
            icon_html = f'<img src="{icon_src}" alt="" aria-hidden="true">'
        else:
            icon_html = f"<span>{html.escape(label[:2], quote=True)}</span>"
        items.append(
            f'<a class="contact-link" href="{url_attr}" title="{label_attr}" '
            f'aria-label="{label_attr}">{icon_html}<span class="contact-label">{label_attr}</span></a>'
        )
    if not items:
        return f"<p>{render_inline(text)}</p>"
    return '<nav class="contact-icons" aria-label="Contact links">' + "".join(items) + "</nav>"


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

        bullet = re.match(r"^[-*+]\s+(.+)$", line)
        if bullet:
            flush_paragraph()
            list_items.append(render_inline(bullet.group(1).strip()))
            continue

        paragraph.append(line)

    flush_paragraph()
    flush_list()
    return Page(title=title, body="\n".join(blocks), sidebar="\n".join(sidebar_blocks))


def render_html(page: Page) -> str:
    title = html.escape(page.title)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div class="layout">
    <aside class="sidebar">
{page.sidebar}
    </aside>
    <main class="page">
{page.body}
    </main>
  </div>
</body>
</html>
"""


def build() -> None:
    source = CONTENT_PATH.read_text(encoding="utf-8")
    page = render_markdown(source)

    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True)

    (DIST_DIR / "index.html").write_text(render_html(page), encoding="utf-8")
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the resume static site.")
    parser.parse_args()
    build()
    print(f"Built {DIST_DIR / 'index.html'}")


if __name__ == "__main__":
    main()
