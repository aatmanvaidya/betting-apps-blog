"""Local server for the betting-apps story.

    uv run betting-apps-blog            # http://127.0.0.1:8000
    uv run betting-apps-blog --port 9000

The page is rebuilt from site/src/index.html on every request, so edits to the
template show up on refresh.
"""
import argparse

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .build import SITE, render_document, write

app = FastAPI(title="Win Guaranteed, Withdrawal Pending", docs_url=None, redoc_url=None)


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return render_document()


@app.get("/healthz")
def healthz() -> dict:
    return {"ok": True}


app.mount("/assets", StaticFiles(directory=SITE / "assets"), name="assets")


def main() -> None:
    import uvicorn

    parser = argparse.ArgumentParser(description="Serve the betting-apps story locally.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--build", action="store_true", help="write site/index.html for publishing and exit")
    args = parser.parse_args()
    if args.build:
        print("wrote", write())
        return
    uvicorn.run(app, host=args.host, port=args.port)
