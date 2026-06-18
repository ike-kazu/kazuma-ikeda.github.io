---
title: Your post title here
date: 2026-06-18
summary: One sentence shown in the blog list and on the home page. Keep it short.
lang: en
---

<!--
HOW TO USE THIS TEMPLATE
1. Copy this file into  posts/  and rename it. The filename (without .md) becomes the URL,
   so use lowercase words separated by hyphens, e.g.  posts/lidar-ghost-points.md  ->  lidar-ghost-points.html
2. Fill in the front matter above (between the --- lines):
      title    required  - shown as the page <h1> and in lists
      date     required  - YYYY-MM-DD. Posts are sorted newest first by this date.
      summary  optional  - one line shown in the post lists
      lang     optional  - "en" (default) or "ja"
3. Write the body in Markdown below. Delete this comment and the examples you don't need.
4. Rebuild:  uv run python .\build.py    then preview at http://localhost:8000
TIP: a file whose name starts with "_" (e.g. _draft.md) is ignored by the build, so use it for drafts.
-->

Open with a short paragraph that says what the post is about. You can use **bold**, `inline code`,
and [links](https://example.com) inside any paragraph.

## A section heading

Use `##` for sections and `###` for subsections. Body text wraps automatically.

- Bullet lists use `-`, `*`, or `+`
- A second bullet
- A third bullet

1. Numbered lists use `1.`, `2.`, ...
2. The numbers can all be `1.` — order is decided by position
3. Third item

> Use `>` for a blockquote / callout.

### Code

Fence code with triple backticks and an optional language for styling:

```python
def hello(name: str) -> str:
    return f"Hello, {name}!"
```

### Images

Put the image file in  media/  then reference it (alt text becomes the caption):

![A short caption describing the figure](media/your-figure.png)

Close with a wrap-up paragraph.
