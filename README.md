# Resume SSG

Python standard-library static site generator for `resume.md`.

## Build

```powershell
uv run python .\build.py
```

The generated site is written to `site/index.html`.

## Preview

```powershell
uv run python -m http.server 8000 -d site
```

Then open `http://localhost:8000`.

## Edit Content

Update `resume.md`, then run `uv run python .\build.py` again.
