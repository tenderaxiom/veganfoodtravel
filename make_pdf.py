#!/usr/bin/env python3
"""Make the free lead-magnet PDF (static/free/vegan-phrase-cards.pdf) from data/countries.json.

Run locally with Google Chrome installed:  python make_pdf.py
"""
import html
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
e = html.escape
LANG = {"French": "fr", "Spanish": "es", "Spanish (Mexico)": "es-MX", "Italian": "it", "Turkish": "tr",
        "German": "de", "Japanese": "ja", "Greek": "el", "English": "en", "Thai": "th",
        "Sinhala": "si", "Hindi": "hi", "Portuguese": "pt-PT", "Vietnamese": "vi", "Indonesian": "id"}


def main():
    cs = sorted(json.loads((ROOT / "data/countries.json").read_text()), key=lambda c: (c.get("rank") or 99, c["name"]))
    logo = (ROOT / "static/brand/logo.svg").read_text()
    pages = []
    for c in cs:
        name = c["name"][0].upper() + c["name"][1:]
        safe = [d for d in c["dishes"] if d["status"] in ("vegan", "usually")][:5]
        ask = [d for d in c["dishes"] if d["status"] == "ask"][:3]
        roman = f'<p class="roman">{e(c["phrase_roman"])}</p>' if c["phrase_roman"] else ""
        pages.append(f"""<section class="page"><div class="top"><div class="logo">{logo}</div><div class="cn">{e(name)}</div></div>
<div class="card"><div class="tag">Show this to your server · {e(c['phrase_lang'])}</div><p class="phrase" lang="{LANG[c['phrase_lang']]}">{e(c['phrase'])}</p>{roman}</div>
<div class="cols"><div><h3>Order these</h3><ul>{''.join(f"<li><b>{e(d['name'])}</b> <i>{e(d['local'])}</i></li>" for d in safe)}</ul>
{('<h3>Ask for these vegan</h3><ul>' + ''.join(f"<li><b>{e(d['name'])}</b> <i>{e(d['local'])}</i>: {e(d['note'])}</li>" for d in ask) + '</ul>') if ask else ''}</div>
<div><h3>Watch for</h3><ul>{''.join(f'<li>{e(w)}</li>' for w in c['watch'])}</ul><p class="word">Word for vegan: <b>{e(c['word'])}</b></p></div></div>
<p class="foot">veganfoodtravel.com{('/vegan-food-in-' + c['slug'] + '/')} · Recipes vary: always confirm ingredients locally.</p></section>""")
    cover = f"""<section class="page cover"><div class="logo big">{logo}</div><h1>Vegan phrase cards</h1>
<p class="sub">How to order vegan food in {len(cs)} countries</p>
<ol>{''.join(f"<li>{e(c['name'][0].upper() + c['name'][1:])} <span>{e(c['phrase_lang'])}</span></li>" for c in cs)}</ol>
<p class="foot">Save this PDF to your phone before you fly. Free from veganfoodtravel.com · hello@veganfoodtravel.com</p></section>"""
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><style>
@page{{size:A4;margin:0}}*{{box-sizing:border-box}}body{{margin:0;font-family:Inter,system-ui,sans-serif;color:#1d2a22}}
.page{{width:210mm;height:297mm;padding:18mm 16mm;page-break-after:always;position:relative;background:#fbfaf6}}
.top{{display:flex;justify-content:space-between;align-items:center}}.logo svg{{height:13mm;width:auto}}.cn{{font-family:Georgia,serif;font-size:30pt;font-weight:700;color:#2f6b45}}
.card{{margin:12mm 0 10mm;border:2.5px dashed #2f6b45;border-radius:7mm;padding:10mm 10mm 8mm;background:#fff;position:relative}}
.tag{{position:absolute;top:-4mm;left:8mm;background:#2f6b45;color:#fff;font-size:9pt;font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:1mm 3mm;border-radius:4mm}}
.phrase{{font-size:21pt;line-height:1.45;margin:0;font-family:"Noto Sans CJK JP","Noto Sans",Inter,sans-serif}}.roman{{color:#5b6b60;font-size:12pt;margin:4mm 0 0}}
.cols{{display:grid;grid-template-columns:1fr 1fr;gap:9mm;font-size:11.5pt}}h3{{font-family:Georgia,serif;color:#2f6b45;font-size:15pt;margin:0 0 2mm}}ul{{padding-left:5mm;margin:0 0 6mm}}li{{margin:1.6mm 0}}i{{color:#5b6b60}}
.word{{background:#e3f1e6;border-radius:3mm;padding:3mm 4mm}}.foot{{position:absolute;bottom:12mm;left:16mm;right:16mm;font-size:9pt;color:#5b6b60;border-top:1px solid #e5e2d8;padding-top:3mm}}
.cover{{background:linear-gradient(160deg,#2f6b45,#1d3f2b);color:#fff}}.cover .logo svg{{height:18mm;background:#fbfaf6;border-radius:4mm;padding:2mm 4mm}}
.cover h1{{font-family:Georgia,serif;font-size:46pt;margin:40mm 0 4mm}}.cover .sub{{font-size:16pt;color:#d9e8de;margin:0 0 14mm}}
.cover ol{{columns:2;font-size:14pt;line-height:2}}.cover ol span{{color:#bfe3c9;font-size:11pt}}.cover .foot{{color:#d9e8de;border-color:#3d6b4f}}
</style></head><body>{cover}{''.join(pages)}</body></html>"""
    out = ROOT / "static/free/vegan-phrase-cards.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        f.write(doc)
    subprocess.run(["google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={out}", f"file://{f.name}"], check=True, capture_output=True)
    print("wrote", out, out.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
