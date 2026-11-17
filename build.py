#!/usr/bin/env python3
"""Static site generator for Vegan Food Travel.

One hub page per country at /vegan-food-in-<slug>/, built from data/countries.json.
A country is indexable only when its "verified" flag is true (checked first-hand);
until then it carries noindex and stays out of the sitemap, so the site never
publishes thin, unchecked pages at scale.
"""
import html
import json
import shutil
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "dist"
SITE = "https://veganfoodtravel.com"
BRAND = "Vegan Food Travel"
TAGLINE = "Eat like a local. Stay vegan."
DESCRIPTOR = "The local food of every country, vegan by tradition."
AUTHOR = "Richard Prouse"
TODAY = date.today().isoformat()
YEAR = date.today().year

STATUS = {
    "vegan": ("Vegan by tradition", "s-vegan"),
    "usually": ("Usually vegan: check", "s-usually"),
    "ask": ("Ask for it vegan", "s-ask"),
    "no": ("Not vegan as standard", "s-no"),
}

e = html.escape


def country_path(c):
    return f"/vegan-food-in-{c['slug']}/"


def display(c):
    return c["name"]


def title_name(c):
    n = c["name"]
    return n[0].upper() + n[1:]


CSS = """
:root{--bg:#fbfaf6;--ink:#1d2a22;--muted:#5b6b60;--line:#e3e1d8;--brand:#2f6b45;--card:#fff;
--vegan:#e3f1e6;--vegan-ink:#1f5a32;--usually:#eef3df;--usually-ink:#4b5a1c;--ask:#fbf0d9;--ask-ink:#7a4f07;--no:#f7e3e0;--no-ink:#8a2a1e}
@media (prefers-color-scheme:dark){:root{--bg:#141a16;--ink:#e8eee9;--muted:#a3b2a8;--line:#2c3630;--brand:#7cc596;--card:#1b231e;
--vegan:#1e3a28;--vegan-ink:#b6e6c4;--usually:#2c3519;--usually-ink:#d9e6a8;--ask:#3a2d12;--ask-ink:#f3d28c;--no:#3d1f1b;--no-ink:#f4b6aa}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
a{color:var(--brand)}a:focus-visible{outline:3px solid var(--brand);outline-offset:2px}
.wrap{max-width:860px;margin:0 auto;padding:0 20px}
header.site{border-bottom:1px solid var(--line)}header.site .wrap{display:flex;justify-content:space-between;align-items:center;padding:14px 20px}
.logo{font-weight:700;text-decoration:none;color:var(--ink);letter-spacing:-.01em}.logo span{color:var(--brand)}
nav a{margin-left:16px;text-decoration:none;color:var(--muted)}
.crumbs{font-size:14px;color:var(--muted);margin:18px 0 0}.crumbs a{color:var(--muted)}
h1{font-size:clamp(30px,6vw,46px);line-height:1.1;letter-spacing:-.02em;margin:28px 0 12px}
h2{font-size:24px;margin:40px 0 12px;letter-spacing:-.01em}
.lead{font-size:19px;color:var(--ink)}
.meta{font-size:14px;color:var(--muted)}
.draft{background:var(--ask);color:var(--ask-ink);border-radius:8px;padding:10px 14px;font-size:14px;margin:16px 0}
.glance{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:22px 0}
.glance div{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.glance b{display:block;font-size:13px;color:var(--muted);font-weight:600;text-transform:uppercase;letter-spacing:.04em}
.dishes{list-style:none;padding:0;display:grid;gap:12px}
.dish{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}
.dish h3{margin:0 0 2px;font-size:19px}.dish .local{color:var(--muted);font-size:15px;margin:0 0 8px}
.dish p{margin:8px 0 0}
.badge{display:inline-block;font-size:13px;font-weight:600;border-radius:999px;padding:2px 10px}
.s-vegan{background:var(--vegan);color:var(--vegan-ink)}.s-usually{background:var(--usually);color:var(--usually-ink)}
.s-ask{background:var(--ask);color:var(--ask-ink)}.s-no{background:var(--no);color:var(--no-ink)}
.phrase{background:var(--card);border:2px dashed var(--brand);border-radius:12px;padding:18px;font-size:20px;line-height:1.5}
.phrase .roman{display:block;font-size:15px;color:var(--muted);margin-top:8px}
.watch li{margin:4px 0}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px;padding:0;list-style:none}
.grid a{display:block;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;text-decoration:none;color:var(--ink);height:100%}
.grid a span{display:block}.grid .n{margin:4px 0}.grid a:hover{border-color:var(--brand)}.grid .n{font-size:20px;font-weight:700}.grid .m{font-size:14px;color:var(--muted)}
.cta{display:inline-block;background:var(--brand);color:#fff;text-decoration:none;font-weight:600;padding:12px 20px;border-radius:999px}
.next{display:flex;justify-content:space-between;gap:12px;margin:40px 0;font-size:15px}
footer{border-top:1px solid var(--line);margin-top:50px;padding:24px 0;font-size:14px;color:var(--muted)}
@media print{header.site,nav,.next,footer,.draft{display:none}body{background:#fff;color:#000}}
"""


def page(*, path, title, description, body, jsonld, indexable, lang="en"):
    canonical = SITE + path
    robots = "index,follow,max-image-preview:large" if indexable else "noindex,follow"
    ld = "\n".join(
        f'<script type="application/ld+json">{json.dumps(obj, ensure_ascii=False)}</script>' for obj in jsonld
    )
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{canonical}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#2f6b45">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<style>{CSS}</style>
{ld}
</head>
<body>
<header class="site"><div class="wrap"><a class="logo" href="/">Vegan <span>Food</span> Travel</a>
<nav aria-label="Main"><a href="/#countries">Countries</a><a href="/about/">About</a></nav></div></header>
<main class="wrap">
{body}
</main>
<footer><div class="wrap">{BRAND}. {e(TAGLINE)} Dish notes are first-hand where marked with a check date. Some links may be affiliate links; they never decide what I recommend. <a href="/about/">How I check</a>.</div></footer>
</body>
</html>
"""


def org():
    return {"@type": "Organization", "@id": SITE + "/#org", "name": BRAND, "url": SITE + "/",
            "logo": SITE + "/favicon.svg", "slogan": TAGLINE,
            "founder": {"@type": "Person", "name": AUTHOR, "url": SITE + "/about/"}}


def person():
    return {"@type": "Person", "@id": SITE + "/about/#author", "name": AUTHOR, "url": SITE + "/about/",
            "jobTitle": "Founder", "worksFor": {"@id": SITE + "/#org"}}


def breadcrumb(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + p}
                                for i, (n, p) in enumerate(items)]}


def country_page(c, countries, i):
    name = display(c)
    tname = title_name(c)
    path = country_path(c)
    n_vegan = sum(1 for d in c["dishes"] if d["status"] in ("vegan", "usually"))
    title = f"Vegan Food in {c.get('short', name)}: {len(c['dishes'])} Local Dishes and What to Ask For ({YEAR})"
    description = (f"Vegan food in {name}: {n_vegan} traditional dishes that are vegan or usually vegan, "
                   f"what to watch for, and a {c['phrase_lang']} phrase card.")[:158]
    checked = c.get("checked")
    aka = f" (also known as {c['aka']})" if c.get("aka") else ""

    dishes_html = "\n".join(
        f"""<li class="dish" id="{e(d['name'].lower().replace(' ', '-'))}"><h3>{e(d['name'])}</h3>
<p class="local">{e(d['local'])}</p><span class="badge {STATUS[d['status']][1]}">{STATUS[d['status']][0]}</span>
<p>{e(d['note'])}</p></li>""" for d in c["dishes"])
    watch_html = "\n".join(f"<li>{e(w)}</li>" for w in c["watch"])
    phrase_lang_code = {"French": "fr", "Spanish": "es", "Spanish (Mexico)": "es-MX", "Italian": "it",
                        "Turkish": "tr", "German": "de", "Japanese": "ja", "Greek": "el", "English": "en"}[c["phrase_lang"]]
    roman = f'<span class="roman" lang="{phrase_lang_code}-Latn">{e(c["phrase_roman"])}</span>' if c["phrase_roman"] else ""
    prev_c = countries[i - 1] if i > 0 else None
    next_c = countries[i + 1] if i + 1 < len(countries) else None
    nav = '<nav class="next" aria-label="More countries">' + (
        f'<a href="{country_path(prev_c)}">&larr; Vegan food in {e(display(prev_c))}</a>' if prev_c else "<span></span>") + (
        f'<a href="{country_path(next_c)}">Vegan food in {e(display(next_c))} &rarr;</a>' if next_c else "<span></span>") + "</nav>"
    draft = "" if c["verified"] else (
        '<p class="draft" role="note"><b>Draft.</b> This guide has not yet been checked on the ground. '
        'It is hidden from search engines until it is.</p>')
    check_line = f"Last checked in {name}: {checked}" if checked else "Not yet checked on the ground"

    body = f"""<p class="crumbs"><a href="/">Home</a> / <a href="/#countries">Countries</a> / {e(tname)}</p>
<article>
<h1>Vegan Food in {e(name)}</h1>
<p class="meta">By <a href="/about/">{AUTHOR}</a> · {check_line} · Updated {TODAY}</p>
{draft}
<p class="lead">{e(c['summary'])}</p>
<div class="glance" aria-label="{e(tname)} at a glance">
<div><b>How easy</b>{e(c['ease'])}</div>
<div><b>Word for vegan</b>{e(c['word'])}</div>
<div><b>Try first</b>{e(c['first_dish'])}</div>
</div>

<h2 id="dishes">Traditional dishes in {e(name)} that are vegan or can be</h2>
<ul class="dishes">
{dishes_html}
</ul>

<h2 id="watch">What to watch for in {e(name)}</h2>
<ul class="watch">
{watch_html}
</ul>

<h2 id="phrase">How to ask for vegan food in {e(c['phrase_lang'])}</h2>
<p>Show this to your server, or print it:</p>
<p class="phrase" lang="{phrase_lang_code}">{e(c['phrase'])}{roman}</p>

<h2 id="why">Why {e(name)}{aka}</h2>
<p>{e(tname)} is the number {c['rank']} most-visited country in the world, with {c['arrivals_m']} million international arrivals in 2024 (UN Tourism).</p>
</article>
{nav}"""

    item_list = {"@type": "ItemList", "name": f"Traditional dishes in {name} that are vegan or can be",
                 "itemListElement": [{"@type": "ListItem", "position": k + 1,
                                      "item": {"@type": "Thing", "name": d["name"], "alternateName": d["local"],
                                               "description": f"{STATUS[d['status']][0]}. {d['note']}"}}
                                     for k, d in enumerate(c["dishes"])]}
    article = {"@context": "https://schema.org", "@type": "Article", "headline": f"Vegan Food in {name}",
               "description": description, "inLanguage": "en", "dateModified": TODAY,
               "mainEntityOfPage": SITE + path, "author": person(), "publisher": org(),
               "about": {"@type": "Country", "name": c.get("aka") or tname.replace("The ", "")},
               "mainEntity": item_list}
    if checked:
        article["datePublished"] = checked
    crumbs = breadcrumb([("Home", "/"), ("Countries", "/#countries"), (tname, path)])
    return path, page(path=path, title=title, description=description, body=body,
                      jsonld=[article, crumbs], indexable=c["verified"])


def home(countries):
    cards = "\n".join(
        f'<li><a href="{country_path(c)}"><span class="m">#{c["rank"]} most visited</span>'
        f'<span class="n">Vegan food in {e(display(c))}</span>'
        f'<span class="m">{e(c["first_dish"])} · {e(c["ease"])}</span></a></li>' for c in countries)
    body = f"""<h1>Eat like a local. Stay vegan.</h1>
<p class="lead">The traditional dishes of every country that are already vegan, the ones you can ask for, and exactly how to ask. From nearly 30 years of travel and 16 years vegan.</p>
<p><a class="cta" href="#countries">Get the phrase card for your next trip</a></p>
<h2 id="countries">The 10 most-visited countries</h2>
<p class="meta">Ranked by international arrivals in 2024 (UN Tourism).</p>
<ul class="grid">
{cards}
</ul>"""
    website = {"@context": "https://schema.org", "@type": "WebSite", "@id": SITE + "/#website", "name": BRAND,
               "url": SITE + "/", "description": DESCRIPTOR, "inLanguage": "en", "publisher": {"@id": SITE + "/#org"}}
    o = {"@context": "https://schema.org", **org()}
    return "/", page(path="/", title=f"{BRAND}: Eat Like a Local, Stay Vegan, in Every Country",
                     description="Traditional dishes that are vegan by tradition, what to watch for, and local-language phrase cards for the world's most-visited countries.",
                     body=body, jsonld=[website, o], indexable=True)


def about():
    body = f"""<p class="crumbs"><a href="/">Home</a> / About</p>
<h1>I've been eating my way around the world for nearly 30 years. For the last 16, I've done it vegan.</h1>
<p class="lead">I'm {AUTHOR}. I started travelling with the Royal New Zealand Navy and never really stopped. Food was always the reason to go. When I went vegan, people assumed that part of travel was over. It wasn't. In most countries, some of the best traditional dishes are already vegan. You just need to know which ones, and how to ask.</p>
<p>That gap, between what vegan travellers fear and what is actually on the table, is what {BRAND} closes. Each guide covers one country: the dishes that are vegan by tradition, the ones you can ask for vegan, what to watch for, and a card in the local language to show your server.</p>
<h2>How each guide is checked</h2>
<ul>
<li>I eat the dishes in the country, and each guide shows the month I last checked it.</li>
<li>Guides I haven't checked first-hand are marked as drafts and hidden from search engines.</li>
<li>Nobody pays to be included. Some links earn a commission; they never decide what I recommend.</li>
<li>If something has changed, tell me. Corrections are dated on the page.</li>
</ul>"""
    p = {"@context": "https://schema.org", "@type": "AboutPage", "url": SITE + "/about/",
         "mainEntity": person(), "publisher": org()}
    return "/about/", page(path="/about/", title=f"About {BRAND}: Nearly 30 Years of Travel, 16 Years Vegan",
                           description=f"{AUTHOR} has travelled to dozens of countries over nearly 30 years and has been vegan for 16. How each {BRAND} guide is checked.",
                           body=body, jsonld=[p], indexable=True)


ROBOTS = f"""# {BRAND}: search engines and AI search crawlers are welcome.
User-agent: *
Allow: /

# AI search and citation crawlers (explicitly allowed)
User-agent: OAI-SearchBot
Allow: /
User-agent: ChatGPT-User
Allow: /
User-agent: Claude-SearchBot
Allow: /
User-agent: Claude-User
Allow: /
User-agent: PerplexityBot
Allow: /
User-agent: Perplexity-User
Allow: /

Sitemap: {SITE}/sitemap.xml
"""

FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><circle cx="32" cy="32" r="30" fill="#2f6b45"/><path d="M20 40c0-12 10-22 26-22-2 14-10 24-22 24-1.5 0-2.8-.6-4-2z" fill="#fbfaf6"/></svg>"""

HEADERS = """/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Content-Security-Policy: default-src 'self'; style-src 'unsafe-inline'; img-src 'self' data:; script-src 'none'; base-uri 'self'; form-action 'self'
"""


def build():
    countries = sorted(json.loads((ROOT / "data/countries.json").read_text()), key=lambda c: c["rank"])
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    pages = [home(countries), about()] + [country_page(c, countries, i) for i, c in enumerate(countries)]
    for path, content in pages:
        target = OUT / path.strip("/") / "index.html" if path != "/" else OUT / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
    indexable = ["/", "/about/"] + [country_path(c) for c in countries if c["verified"]]
    sm = "\n".join(f"  <url><loc>{SITE}{p}</loc><lastmod>{TODAY}</lastmod></url>" for p in indexable)
    (OUT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sm}\n</urlset>\n')
    (OUT / "robots.txt").write_text(ROBOTS)
    (OUT / "favicon.svg").write_text(FAVICON)
    (OUT / "_headers").write_text(HEADERS)
    (OUT / "404.html").write_text(page(path="/404", title="Page not found", description="Page not found.",
                                       body='<h1>Page not found</h1><p><a href="/">See all countries</a></p>',
                                       jsonld=[], indexable=False))
    print(f"Built {len(pages)} pages; {len(indexable)} indexable; {sum(not c["verified"] for c in countries)} drafts hidden.")


if __name__ == "__main__":
    build()
