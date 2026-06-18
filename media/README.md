# media/

Put teaser images for the Publications showcase and images used in blog posts here.
Everything in this folder is copied verbatim to `site/media/` at build time.

Reference them with a root-relative-to-site path, e.g. in `featured.md`:

```
image: media/ghost-fwl.png
```

or inside a blog post in `posts/`:

```
![Result figure](media/my-figure.png)
```

A featured card whose `image:` file does not exist yet renders text-only, so it is safe to
list an image before adding the file.
