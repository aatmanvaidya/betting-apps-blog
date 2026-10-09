"""Write site/index.html (the page to publish) and site/_preview.html (a standalone copy).

    uv run python scripts/build_html.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from betting_apps_blog.build import write  # noqa: E402

print("wrote", write())
