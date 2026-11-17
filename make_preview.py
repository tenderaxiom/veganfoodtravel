#!/usr/bin/env python3
"""Bundle dist/ into one preview.html (hash-routed) for review; the real site stays multi-page."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
pages = {"home": DIST / "index.html", "about": DIST / "about/index.html"}
for d in sorted(DIST.glob("vegan-food-in-*")):
    pages[d.name] = d / "index.html"


def main_of(p):
    s = p.read_text()
    return re.search(r"<main class=\"wrap\">(.*)</main>", s, re.S).group(1)


def relink(s):
    s = re.sub(r'href="/(vegan-food-in-[a-z-]+)/"', r'href="#\1"', s)
    s = s.replace('href="/about/"', 'href="#about"').replace('href="/#countries"', 'href="#home"')
    return s.replace('href="/"', 'href="#home"')


home = (DIST / "index.html").read_text()
css = re.search(r"<style>(.*?)</style>", home, re.S).group(1)
sections = "\n".join(
    f'<section id="{k}" class="pg" hidden>{relink(main_of(p))}</section>' for k, p in pages.items())
html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Vegan Food Travel: site preview</title><style>{css}
.pv{{background:#2f6b45;color:#fff;font-size:13px;padding:6px 20px;text-align:center}}</style></head>
<body><div class="pv">Preview of veganfoodtravel.com (not yet live). Country guides are drafts until checked on the ground.</div>
<header class="site"><div class="wrap"><a class="logo" href="#home">Vegan <span>Food</span> Travel</a>
<nav aria-label="Main"><a href="#home">Countries</a><a href="#about">About</a></nav></div></header>
<main class="wrap">{sections}</main>
<footer><div class="wrap">Vegan Food Travel: The local food of every country, vegan by tradition.</div></footer>
<script>
function show(){{var id=(location.hash||'#home').slice(1);var el=document.getElementById(id);if(!el||!el.classList.contains('pg'))id='home';
document.querySelectorAll('.pg').forEach(function(s){{s.hidden=s.id!==id}});window.scrollTo(0,0);}}
addEventListener('hashchange',show);show();
</script></body></html>"""
(ROOT / "preview.html").write_text(html)
print("preview.html", len(html), "bytes,", len(pages), "pages")
