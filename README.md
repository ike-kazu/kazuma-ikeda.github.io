# Personal site SSG

Python standard-library static site generator. Builds a multi-page personal site:

- **Home** (`index.html`) — profile/resume from `resume.md` plus the latest blog posts
- **Publications** (`publications.html`) — a figure-based featured showcase plus the full
  publication list, grouped by year
- **Blog** (`blog.html` + one page per post) — posts written in `posts/`

## Build

```powershell
uv run python .\build.py
```

The generated site is written to `site/` (and a clean one-page `resume.pdf`).

## Preview

```powershell
uv run python -m http.server 8000 -d site
```

Then open `http://localhost:8000`.

## Edit content

> Full authoring reference: **[CONTENT.md](CONTENT.md)**. Copy-paste starting points live in
> [`templates/`](templates/) (`post-template.md`, `featured-entry.md`).

### Profile / resume

Update `resume.md`, then rebuild. The home sidebar, the resume body, and the full publication
list on the Publications page are all generated from this file. The `resume.pdf` is the home
page printed to PDF (the nav and "Latest posts" sections are hidden in print).

### Blog posts

Add a Markdown file to `posts/` with front matter:

```markdown
---
title: My post title
date: 2026-06-18
summary: One-line summary shown in the post lists.
lang: en
---

Body in Markdown. Headings, lists, **bold**, `code`, links, images,
fenced ```code blocks```, and > blockquotes are supported.
```

The filename stem becomes the URL slug (`posts/hello-world.md` → `hello-world.html`).
Posts are sorted by `date` (newest first).

### Publications showcase

The full year-grouped list comes straight from `resume.md` (no duplication). To feature a few
papers with a teaser image and links, edit `featured.md` — see the comments in that file.
Put teaser images and post images in `media/` (copied to `site/media/`).
