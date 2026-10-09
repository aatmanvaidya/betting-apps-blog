"""Build dist/, the self-contained folder to deploy (Netlify etc.).

    uv run python scripts/build_dist.py

Copies site/assets/ and writes dist/index.html as a full HTML document.
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from betting_apps_blog.build import render, render_document  # noqa: E402

DIST = ROOT / "dist"
shutil.rmtree(DIST, ignore_errors=True)
DIST.mkdir()
shutil.copytree(ROOT / "site" / "assets", DIST / "assets")
(DIST / "index.html").write_text(render_document(render()), encoding="utf-8")
print("wrote", DIST)
