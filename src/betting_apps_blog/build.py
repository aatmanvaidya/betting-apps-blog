"""Assemble the story page: inject the data files into the HTML template."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "site"

# Pages that look like private individuals (or phone numbers) are withheld on the page.
PERSON_PAGES = {
    "Risner Smith Taschner", "Bowen Paxton Ian", "Henry Ella Durso", "Jeremy Grey3", "Ofei",
    "Alexa Rivera Cambria", "Eric Wright", "Himanshu Sharma", "Ankit Jain Aviator", "Spurdha Choudhary Fagna",
    "Beatrice b", "Hernandez Zach Katie", "Kapil Gupta", "malik_mumbai__03", "ramchoudhary5500", "patrick_umam",
}
PHONE = re.compile(r"\+?\d[\d\s-]{8,}\d")


def _manifest():
    manifest = json.loads((SITE / "assets" / "manifest.json").read_text())
    for m in manifest["ads"].values():
        page = m.get("page", "")
        if page.isdigit():
            m["page"], m["masked"] = "A page named with a phone number", True
        elif page in PERSON_PAGES:
            m["page"], m["masked"] = "A page named after a person", True
        for k in ("title", "body"):
            if m.get(k):
                m[k] = PHONE.sub("[number removed]", m[k])
    return manifest


def render() -> str:
    """Return the page body (what gets published as the artifact's index.html)."""
    tpl = (SITE / "src" / "index.html").read_text(encoding="utf-8")
    data = {
        "__MANIFEST__": _manifest(),
        "__IG_DATA__": json.loads((SITE / "data" / "ig_inline.json").read_text()),
        "__DERIVED__": json.loads((SITE / "data" / "derived.json").read_text()),
    }
    for key, value in data.items():
        tpl = tpl.replace(key, json.dumps(value, ensure_ascii=False, separators=(",", ":")))
    return tpl


def render_document(body: str | None = None) -> str:
    """Wrap the page in the same skeleton the artifact host adds, for local viewing."""
    body = render() if body is None else body
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
            '<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top);padding-bottom:env(safe-area-inset-bottom)}'
            'body{margin:0;font:14px system-ui,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>'
            '</head><body>' + body + '</body></html>')


def write() -> Path:
    body = render()
    out = SITE / "index.html"
    out.write_text(body, encoding="utf-8")
    (SITE / "_preview.html").write_text(render_document(body), encoding="utf-8")
    return out
