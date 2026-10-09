# Win Guaranteed, Withdrawal Pending

A scrolling data story for *Quantifying the Illicit Ecosystem of Betting Apps in India* (Aatman Vaidya, Kiran Garimella).

## Run it locally

```sh
uv sync
uv run betting-apps-blog          # http://127.0.0.1:8000
```

The FastAPI app (`src/betting_apps_blog/`) rebuilds the page from `site/src/index.html` on every request, so edits show up on refresh. Use `--port` to change the port.

## Layout

- `site/src/index.html` – the page template (CSS, markup, scripts)
- `site/data/` – derived stats and Instagram annotations injected into the page
- `site/assets/` – ad images, video clips, halftone posters, Instagram posts, `manifest.json`
- `scripts/build_assets.py` – rebuilds `site/assets/` from the research media on the external volume
- `scripts/build_html.py` – writes `site/index.html` (the file that gets published) and `site/_preview.html`
- `scripts/category_examples.json`, `scripts/instagram_picks.json` – which ads and posts appear on the page
