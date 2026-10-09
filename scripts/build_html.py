"""Inject data files into the HTML template and write site/index.html."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(HERE, "..", "site")

PERSON_PAGES = {
    "Risner Smith Taschner", "Bowen Paxton Ian", "Henry Ella Durso", "Jeremy Grey3", "Ofei",
    "Alexa Rivera Cambria", "Eric Wright", "Himanshu Sharma", "Ankit Jain Aviator", "Spurdha Choudhary Fagna",
}

manifest = json.load(open(os.path.join(SITE, "assets", "manifest.json")))
for name, m in manifest["ads"].items():
    page = m.get("page", "")
    if page.isdigit():
        m["page"] = "A page named with a phone number"
        m["masked"] = True
    elif page in PERSON_PAGES:
        m["page"] = "A page named after a person"
        m["masked"] = True
    m.pop("src", None)
    m.pop("id", None)
    if name == "lotus_ipl_id":
        m["body"] = "👇 WhatsApp now to get your ID 👇 [phone number removed]"

ig = json.load(open(os.path.join(SITE, "data", "ig_inline.json")))
derived = json.load(open(os.path.join(SITE, "data", "derived.json")))

tpl = open(os.path.join(SITE, "src", "index.html"), encoding="utf-8").read()
out = (tpl.replace("__MANIFEST__", json.dumps(manifest, ensure_ascii=False, separators=(",", ":")))
          .replace("__IG_DATA__", json.dumps(ig, ensure_ascii=False, separators=(",", ":")))
          .replace("__DERIVED__", json.dumps(derived, ensure_ascii=False, separators=(",", ":"))))
open(os.path.join(SITE, "index.html"), "w", encoding="utf-8").write(out)
print("wrote site/index.html", len(out) // 1024, "KB")

# Local preview: mimic the artifact skeleton (doctype, viewport, small reset) so the page renders the same way.
preview = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
           '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
           '<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top);padding-bottom:env(safe-area-inset-bottom)}'
           'body{margin:0;font:14px system-ui,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>'
           '</head><body>' + out + '</body></html>')
open(os.path.join(SITE, "_preview.html"), "w", encoding="utf-8").write(preview)
