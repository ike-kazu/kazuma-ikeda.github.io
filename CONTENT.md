# Content guide

How to add and edit content on this site. The site is built by `build.py` from plain
Markdown/text files — no database, no framework. After any change, run:

```powershell
uv run python .\build.py                       # build into site/
uv run python -m http.server 8000 -d site      # preview at http://localhost:8000
```

Templates to copy from live in `templates/`.

---

## Where each thing comes from

| Page | Output | Source file(s) |
| --- | --- | --- |
| Home (profile + latest posts) | `site/index.html` | `resume.md`, newest `posts/*.md` |
| Publications | `site/publications.html` | `resume.md` (full list) + `featured.md` (showcase) |
| Blog list | `site/blog.html` | all `posts/*.md` |
| A blog post | `site/<slug>.html` | `posts/<slug>.md` |
| Resume PDF | `site/resume.pdf` | the Home page, printed (nav & latest posts hidden) |
| Images / teasers | `site/media/...` | `media/` (copied verbatim) |

---

## Add a blog post

1. Copy `templates/post-template.md` into `posts/` and rename it. **The filename becomes the
   URL**, so use lowercase hyphenated words: `posts/lidar-ghost-points.md` → `lidar-ghost-points.html`.
2. Fill in the front matter (the block between the `---` lines at the top):

   | Field | Required | Notes |
   | --- | --- | --- |
   | `title` | yes | Shown as the page heading and in lists |
   | `date` | yes | `YYYY-MM-DD`. Posts sort newest-first by this date |
   | `summary` | no | One line shown in the blog list and on the home page |
   | `lang` | no | `en` (default) or `ja` |

3. Write the body in Markdown (see supported syntax below).
4. Rebuild and preview.

The newest **3** posts also appear in the "Latest posts" section on the home page
(change `LATEST_POSTS_COUNT` in `build.py` to show more or fewer).

**Drafts:** a file whose name starts with `_` (e.g. `posts/_wip.md`) is ignored by the build —
rename it to publish.

### Supported Markdown in posts

| Syntax | Result |
| --- | --- |
| `# … ######` | Headings (`##` for sections, `###` for subsections) |
| `**bold**` | **bold** |
| `` `code` `` | inline code |
| `[text](url)` | link |
| `- ` / `* ` / `+ ` | bullet list |
| `1. ` | numbered list |
| `> quote` | blockquote / callout |
| ` ```lang ` … ` ``` ` | fenced code block (language label optional, used for styling) |
| `![caption](media/img.png)` | image; the alt text becomes the caption |

> This is a deliberately small Markdown subset. Tables and raw HTML are **not** rendered —
> if you need something more, extend `render_body()` in `build.py`.

---

## Feature a publication (showcase)

The **full** year-grouped list on the Publications page is generated automatically from the
`## International Publications & Conferences` and `## Domestic Conferences` sections of
`resume.md`. To **add or edit a publication, edit `resume.md`** — nothing else needed.

To **highlight** a paper with a teaser image and link buttons at the top of the page, add a
block to `featured.md` (copy from `templates/featured-entry.md`):

```
## Ghost-FWL: A Large-Scale Full-Waveform LiDAR Dataset ...
image: media/ghost-fwl.png
venue: CVPR 2026
blurb: A large-scale full-waveform LiDAR dataset for ghost detection and removal.
PDF: https://example.com/ghost-fwl.pdf
Code: https://github.com/your/repo
Project: https://your-project-page.example.com
```

- The `## Heading` text matches (case-insensitive substring) the citation in `resume.md`, so the
  full citation is pulled in automatically — never retype it. Use a `match:` line to override.
- `image:` is optional. **The card shows as text-only until the image file exists**, so it is
  safe to reference an image before you add it.
- Any `Label: url` line other than `image`/`venue`/`blurb`/`match` becomes a link button
  (e.g. `PDF`, `Code`, `Project`, `Video`, `Dataset`, `arXiv`, `Slides`).
- Cards appear in the order listed in `featured.md`.

---

## Images

Put every image in `media/`. The whole folder is copied to `site/media/` on build.

- In `featured.md`:  `image: media/my-teaser.png`
- In a post:  `![Caption](media/my-figure.png)`

Teaser cards look best with a roughly 4:3 or 16:9 image (they are cropped to fill).

---

## Publish

Commit and push to `main`. The GitHub Actions workflow (`.github/workflows/pages.yml`) rebuilds
and deploys to GitHub Pages automatically. No build step is run by hand for deployment.
