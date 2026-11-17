#!/usr/bin/env python3
"""Static site generator for Vegan Food Travel (veganfoodtravel.com).

Builds every page into dist/ from data/countries.json, data/photo_credits.json and static/.
A country guide is indexable only when its "verified" flag is true (checked first-hand);
until then it carries noindex and stays out of the sitemap.
"""
import html
import json
import re
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
EMAIL = "hello@veganfoodtravel.com"
VEGAN_SINCE = 2015
TODAY = date.today().isoformat()
YEAR = date.today().year
YEARS_VEGAN = YEAR - VEGAN_SINCE
INDEXNOW_KEY = "eb83adc9025d4966a4a86c9ed665cae4"
PDF_PATH = "/free/vegan-phrase-cards.pdf"

STATUS = {
    "vegan": ("Vegan by tradition", "s-vegan"),
    "usually": ("Usually vegan: check", "s-usually"),
    "ask": ("Ask for it vegan", "s-ask"),
    "no": ("Not vegan as standard", "s-no"),
}
LANG = {"French": "fr", "Spanish": "es", "Spanish (Mexico)": "es-MX", "Italian": "it", "Turkish": "tr",
        "German": "de", "Japanese": "ja", "Greek": "el", "English": "en"}

e = html.escape
CREDITS = json.loads((ROOT / "data/photo_credits.json").read_text()) if (ROOT / "data/photo_credits.json").exists() else {}


def slugify(s):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")


def country_path(c):
    return f"/vegan-food-in-{c['slug']}/"


def cap(s):
    return s[0].upper() + s[1:]


# ---------------------------------------------------------------- images
def photo(key):
    """Return credit record for a photo key if its files exist, else None."""
    c = CREDITS.get(key)
    if c and (ROOT / "static/img" / f"{c['slug']}-960.webp").exists():
        return c
    return None


def picture(key, alt, sizes, cls="", eager=False, credit=True):
    p = photo(key)
    if not p:
        return f'<div class="ph {cls}" role="img" aria-label="{e(alt)}"></div>'
    s = p["slug"]
    w, h = p["w"], p["h"]
    srcset = ", ".join(f"/img/{s}-{x}.webp {x}w" for x in (480, 960, 1600) if (ROOT / f"static/img/{s}-{x}.webp").exists())
    load = 'fetchpriority="high" loading="eager"' if eager else 'loading="lazy" decoding="async"'
    img = (f'<img class="{cls}" src="/img/{s}-960.webp" srcset="{srcset}" sizes="{sizes}" '
           f'width="{w}" height="{h}" alt="{e(alt)}" {load}>')
    if not credit:
        return img
    return img + credit_line(key)


def credit_line(key):
    p = photo(key)
    if not p:
        return ""
    lic = f'<a href="{e(p["license_url"])}" rel="license nofollow">{e(p["license"])}</a>' if p.get("license_url") else e(p["license"])
    return (f'<small class="credit">Photo: <a href="{e(p["page"])}" rel="nofollow">{e(p["author"])}</a>, '
            f'{lic}, resized</small>')


def og_image(key):
    p = photo(key)
    return f"{SITE}/img/{p['slug']}-1600.webp" if p else f"{SITE}/brand/og.png"


# ---------------------------------------------------------------- styles
CSS = """
:root{--bg:#fbfaf6;--ink:#1d2a22;--muted:#5b6b60;--line:#e5e2d8;--brand:#2f6b45;--brand-d:#24553a;--accent:#e9a23b;--card:#fff;
--vegan:#e3f1e6;--vegan-ink:#1f5a32;--usually:#eef3df;--usually-ink:#4b5a1c;--ask:#fbf0d9;--ask-ink:#7a4f07;--no:#f7e3e0;--no-ink:#8a2a1e;
--serif:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;--r:16px;--shadow:0 1px 2px rgba(29,42,34,.06),0 8px 24px rgba(29,42,34,.08)}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.65 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
img{max-width:100%;height:auto;display:block}
a{color:var(--brand)}a:focus-visible,button:focus-visible,input:focus-visible{outline:3px solid var(--accent);outline-offset:2px}
.wrap{max-width:1120px;margin:0 auto;padding:0 20px}.narrow{max-width:760px}
h1,h2,h3{font-family:var(--serif);letter-spacing:-.01em;line-height:1.15}
h1{font-size:clamp(34px,6vw,60px);margin:0 0 14px}h2{font-size:clamp(26px,3.6vw,36px);margin:56px 0 14px}h3{font-size:21px;margin:0 0 4px}
.eyebrow{font-size:13px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--brand)}
.lead{font-size:clamp(18px,2.2vw,21px)}.muted,.meta{color:var(--muted)}.meta{font-size:14px}
header.site{position:sticky;top:0;z-index:20;background:rgba(251,250,246,.92);backdrop-filter:saturate(1.4) blur(10px);border-bottom:1px solid var(--line)}
header.site .wrap{display:flex;justify-content:space-between;align-items:center;height:66px}
.logo img{height:40px;width:auto}nav.main{display:flex;gap:6px;align-items:center}
nav.main a{text-decoration:none;color:var(--ink);font-weight:500;padding:8px 12px;border-radius:999px}nav.main a:hover{background:#eef0ea}
.btn{display:inline-block;background:var(--brand);color:#fff!important;text-decoration:none;font-weight:700;padding:13px 22px;border-radius:999px;border:0;font-size:16px;cursor:pointer;box-shadow:0 6px 16px rgba(47,107,69,.25)}
.btn:hover{background:var(--brand-d)}.btn.sm{padding:9px 16px;font-size:15px;box-shadow:none}.btn.ghost{background:transparent;color:var(--ink)!important;border:2px solid currentColor;box-shadow:none}
@media(max-width:720px){nav.main a:not(.btn){display:none}}
.hero{position:relative;min-height:min(78vh,680px);display:flex;align-items:flex-end;color:#fff;overflow:hidden;background:#24553a}
.hero img,.hero .ph{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.hero::after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(10,25,16,.72),rgba(10,25,16,.25) 70%),linear-gradient(180deg,rgba(0,0,0,0) 40%,rgba(10,25,16,.7))}
.hero h1,.hero .lead{text-shadow:0 2px 14px rgba(0,0,0,.35)}
.hero .wrap{position:relative;z-index:2;padding-bottom:56px;padding-top:120px}.hero .lead{max-width:640px;color:#f3f6f2}
.hero .credit{position:absolute;right:10px;bottom:6px;z-index:3;color:#dfe7e1}.hero .credit a{color:#dfe7e1}
.hero.short{min-height:min(62vh,540px)}.hero .crumbs,.hero .crumbs a{color:#e6efe8}
.ph{background:linear-gradient(135deg,#cfe3d4,#f3e3c3)}
.credit{display:block;font-size:11.5px;line-height:1.4;color:var(--muted);margin-top:6px}.credit a{color:inherit}
.grid{display:grid;gap:22px;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));padding:0;list-style:none;margin:24px 0}
.card{background:var(--card);border-radius:var(--r);overflow:hidden;box-shadow:var(--shadow);display:flex;flex-direction:column;height:100%;text-decoration:none;color:var(--ink);transition:transform .15s ease,box-shadow .15s ease}
a.card:hover{transform:translateY(-3px);box-shadow:0 2px 4px rgba(29,42,34,.08),0 16px 36px rgba(29,42,34,.14)}
.card .media{aspect-ratio:4/3;overflow:hidden;background:#e9eee8}.card .media img,.card .media .ph{width:100%;height:100%;object-fit:cover}
.card .body{padding:16px 18px 18px;display:flex;flex-direction:column;gap:6px;flex:1}.card .credit{padding:0 18px 12px;margin:0}
.card .kicker{font-size:13px;color:var(--muted)}.card .name{font-family:var(--serif);font-size:22px;font-weight:700;line-height:1.2}
.badge{display:inline-block;align-self:flex-start;font-size:13px;font-weight:700;border-radius:999px;padding:3px 11px}
.s-vegan{background:var(--vegan);color:var(--vegan-ink)}.s-usually{background:var(--usually);color:var(--usually-ink)}.s-ask{background:var(--ask);color:var(--ask-ink)}.s-no{background:var(--no);color:var(--no-ink)}
.local{color:var(--muted);font-style:italic;margin:0}
.glance{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px;margin:28px 0}
.glance div{background:var(--card);border-radius:14px;padding:16px 18px;box-shadow:var(--shadow)}
.glance b{display:block;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin-bottom:2px}
.draft{background:var(--ask);color:var(--ask-ink);border-radius:12px;padding:12px 16px;font-size:14px;margin:22px 0}
.more{list-style:none;padding:0;margin:10px 0 26px;background:var(--card);border-radius:16px;box-shadow:var(--shadow);overflow:hidden}
.more li{display:grid;grid-template-columns:minmax(150px,210px) 1fr;gap:6px 18px;padding:14px 20px;border-top:1px solid rgba(0,0,0,.07)}.more li:first-child{border-top:0}
.more h4{margin:0;font-size:17px}.more .local{font-size:14px;margin:2px 0 6px;opacity:.75}.more p{margin:0}
@media (max-width:600px){.more li{grid-template-columns:1fr}}
.regions{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px;margin:14px 0 8px}
.regions div{background:var(--card);border-radius:14px;padding:16px 18px;box-shadow:var(--shadow)}.regions h3{margin:0 0 6px;font-size:18px}.regions p{margin:0}
table.phrases{width:100%;border-collapse:collapse;margin:12px 0 8px;background:var(--card);border-radius:14px;overflow:hidden;box-shadow:var(--shadow)}
table.phrases th,table.phrases td{text-align:left;padding:12px 16px;border-top:1px solid rgba(0,0,0,.07);vertical-align:top}table.phrases th{font-size:14px;border-top:0}
table.phrases .roman{display:block;font-size:14px;opacity:.75;margin-top:2px}
.faq h3{font-size:19px;margin:20px 0 4px}.faq p{margin:0}
.watch{background:var(--card);border-left:5px solid var(--accent);border-radius:12px;padding:18px 22px 18px 40px;box-shadow:var(--shadow)}.watch li{margin:6px 0}
.phrase{position:relative;background:#fffdf7;border:2px dashed var(--brand);border-radius:18px;padding:26px 26px 22px;font-size:clamp(19px,2.4vw,23px);line-height:1.55;box-shadow:var(--shadow)}
.phrase .roman{display:block;font-size:15px;color:var(--muted);margin-top:10px}.phrase .tag{position:absolute;top:-13px;left:20px;background:var(--brand);color:#fff;font-size:12px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;padding:3px 10px;border-radius:999px}
.cta{background:linear-gradient(135deg,#2f6b45,#24553a);color:#fff;border-radius:24px;padding:clamp(26px,4vw,44px);margin:56px 0;display:grid;gap:24px;grid-template-columns:1.2fr 1fr;align-items:center;box-shadow:var(--shadow)}
.cta h2{margin:0 0 8px;color:#fff}.cta p{color:#e3eee6;margin:0}.cta .pack{background:#fffdf7;color:var(--ink);border-radius:16px;padding:18px;transform:rotate(-2deg);box-shadow:0 18px 40px rgba(0,0,0,.25)}
.cta .pack b{font-family:var(--serif);font-size:20px}.cta .pack li{font-size:14px;margin:4px 0}
@media(max-width:760px){.cta{grid-template-columns:1fr}.cta .pack{display:none}}
form.signup{display:flex;flex-wrap:wrap;gap:10px;margin-top:16px}form.signup input[type=email]{flex:1 1 240px;padding:14px 16px;border-radius:999px;border:0;font-size:16px}
form.signup .consent{flex-basis:100%;font-size:13.5px;color:#d8e6dc;display:flex;gap:8px;align-items:flex-start}form.signup .consent input{margin-top:4px}
form.signup .btn{background:var(--accent);color:#1d2a22!important;box-shadow:none}form.signup .btn:hover{background:#f2b453}
.light form.signup input[type=email]{border:2px solid var(--line)}.light form.signup .consent{color:var(--muted)}
.hp{position:absolute;left:-5000px;width:1px;height:1px;overflow:hidden}
.err{background:#f7e3e0;color:#8a2a1e;border-radius:10px;padding:8px 12px;font-size:14px;flex-basis:100%;display:none}.err:target,.show{display:block}
.steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:18px;counter-reset:s;list-style:none;padding:0}
.steps li{background:var(--card);border-radius:var(--r);padding:22px;box-shadow:var(--shadow);counter-increment:s}
.steps li::before{content:counter(s);display:grid;place-items:center;width:34px;height:34px;border-radius:50%;background:var(--vegan);color:var(--vegan-ink);font-weight:800;margin-bottom:10px}
.founder{display:grid;grid-template-columns:auto 1fr;gap:22px;align-items:center;background:var(--card);border-radius:var(--r);padding:24px;box-shadow:var(--shadow)}
.founder .mono{width:84px;height:84px}@media(max-width:560px){.founder{grid-template-columns:1fr}}
.pager{display:flex;justify-content:space-between;gap:12px;margin:48px 0;font-weight:600}.pager a{text-decoration:none}
.crumbs{font-size:14px;margin:0 0 10px}.crumbs a{text-decoration:none}
.prose h2{margin-top:40px}.prose li{margin:6px 0}
.cards-print{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px}
footer.site{background:#1d2a22;color:#c9d6cd;margin-top:80px;padding:44px 0 30px;font-size:15px}
footer.site a{color:#e8f0ea}footer.site .cols{display:grid;grid-template-columns:2fr 1fr 1fr;gap:28px}footer.site h4{color:#fff;margin:0 0 8px;font-size:14px;letter-spacing:.1em;text-transform:uppercase}
footer.site ul{list-style:none;padding:0;margin:0}footer.site li{margin:5px 0}footer.site .fine{border-top:1px solid #2f3d34;margin-top:28px;padding-top:16px;font-size:13px;color:#9fb0a5}
@media(max-width:720px){footer.site .cols{grid-template-columns:1fr}}
@media (prefers-reduced-motion:reduce){*{transition:none!important;scroll-behavior:auto!important}}
@media print{header.site,footer.site,.cta,.pager,.hero,.no-print{display:none!important}body{background:#fff}.phrase{box-shadow:none;break-inside:avoid}}
"""

ERRORS_JS = """<script>(function(){var q=new URLSearchParams(location.search).get('error');if(!q)return;document.querySelectorAll('.err[data-e="'+q+'"]').forEach(function(x){x.classList.add('show')});var f=document.querySelector('form.signup');if(f)f.scrollIntoView({block:'center'})})()</script>"""


def signup_form(source, country=""):
    return f"""<form class="signup" method="post" action="/api/subscribe">
<input type="hidden" name="source" value="{e(source)}"><input type="hidden" name="country" value="{e(country)}">
<label class="hp">Leave this empty <input name="website" tabindex="-1" autocomplete="off"></label>
<label class="sr" for="em-{slugify(source)}" style="position:absolute;left:-5000px">Email address</label>
<input id="em-{slugify(source)}" type="email" name="email" required placeholder="Your email address" autocomplete="email" inputmode="email">
<button class="btn" type="submit">Send me the free pack</button>
<label class="consent"><input type="checkbox" name="consent" value="yes" required> <span>Send me the free phrase-card pack and the weekly email (one country, one dish, one phrase). Unsubscribe any time. <a href="/privacy/">Privacy</a>.</span></label>
<p class="err" data-e="email">Please enter a valid email address.</p><p class="err" data-e="consent">Please tick the box so I can send it.</p>
</form>"""


def cta_block(source, country=""):
    return f"""<section class="cta" aria-labelledby="cta-{slugify(source)}">
<div><p class="eyebrow" style="color:#bfe3c9">Free download</p><h2 id="cta-{slugify(source)}">Never go hungry abroad</h2>
<p>Get the pocket phrase cards for all 10 countries: the vegan sentence in the local language, what to watch for, and the safest dishes to order. Plus one short email a week.</p>
{signup_form(source, country)}</div>
<div class="pack" aria-hidden="true"><b>Vegan phrase cards</b><ul><li>🇫🇷 Je suis végane…</li><li>🇯🇵 私はヴィーガンです…</li><li>🇲🇽 Sin manteca, por favor…</li><li>🇬🇷 Είναι νηστίσιμο;</li><li>+ 6 more countries</li></ul></div>
</section>"""


def page(*, path, title, description, body, jsonld=(), indexable=True, og=None, hero="", narrow=False):
    canonical = SITE + path
    robots = "index,follow,max-image-preview:large" if indexable else "noindex,follow"
    ld = "\n".join(f'<script type="application/ld+json">{json.dumps(o, ensure_ascii=False)}</script>' for o in jsonld)
    og = og or f"{SITE}/brand/og.png"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website"><meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{canonical}"><meta property="og:image" content="{og}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#2f6b45">
<link rel="icon" href="/brand/mark.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/brand/apple-touch-icon.png">
<style>{CSS}</style>
{ld}
</head>
<body>
<header class="site"><div class="wrap"><a class="logo" href="/" aria-label="{BRAND} home"><img src="/brand/logo.svg" alt="{BRAND}" width="206" height="40"></a>
<nav class="main" aria-label="Main"><a href="/#countries">Countries</a><a href="/phrase-cards/">Phrase cards</a><a href="/about/">About</a><a class="btn sm" href="/free-guide/">Free pack</a></nav></div></header>
<main>
{hero}
<div class="wrap{' narrow' if narrow else ''}">
{body}
</div>
</main>
<footer class="site"><div class="wrap"><div class="cols">
<div><img src="/brand/logo-light.svg" alt="{BRAND}" width="230" height="45"><p style="margin-top:12px">{e(DESCRIPTOR)} Written from over 30 years of travel and {YEARS_VEGAN} years vegan.</p></div>
<div><h4>Explore</h4><ul><li><a href="/#countries">All countries</a></li><li><a href="/phrase-cards/">Phrase cards</a></li><li><a href="/free-guide/">Free pack</a></li></ul></div>
<div><h4>About</h4><ul><li><a href="/about/">About &amp; how I check</a></li><li><a href="/contact/">Contact</a></li><li><a href="/privacy/">Privacy</a></li><li><a href="/terms/">Terms &amp; disclosure</a></li><li><a href="/photo-credits/">Photo credits</a></li></ul></div>
</div><p class="fine">© {YEAR} {BRAND}. Nobody pays to be included. Photos are free-licensed from Wikimedia Commons and credited on each page.</p></div></footer>
{ERRORS_JS}
</body>
</html>
"""


def org():
    return {"@type": "Organization", "@id": SITE + "/#org", "name": BRAND, "url": SITE + "/",
            "logo": SITE + "/brand/mark-512.png", "slogan": TAGLINE, "email": EMAIL,
            "founder": {"@type": "Person", "name": AUTHOR, "url": SITE + "/about/"}}


def person():
    return {"@type": "Person", "@id": SITE + "/about/#author", "name": AUTHOR, "url": SITE + "/about/",
            "jobTitle": "Founder", "nationality": "New Zealand", "worksFor": {"@id": SITE + "/#org"},
            "description": f"Travelled for over 30 years, with the Royal New Zealand Navy, on cruise ships and superyachts. Vegan since {VEGAN_SINCE}."}


def breadcrumb(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + p}
                                for i, (n, p) in enumerate(items)]}


# ---------------------------------------------------------------- pages
def hero_block(key, alt, inner, short=False):
    return f"""<section class="hero{' short' if short else ''}">{picture(key, alt, '100vw', eager=True, credit=False)}
<div class="wrap">{inner}</div>{credit_line(key)}</section>"""


def country_page(c, countries, i):
    name, slug = c["name"], c["slug"]
    tname = cap(name)
    path = country_path(c)
    all_dishes = c["dishes"] + c.get("more_dishes", [])
    n_ok = sum(1 for d in all_dishes if d["status"] in ("vegan", "usually"))
    title = f"Vegan Food in {c.get('short', name)}: {len(all_dishes)} Local Dishes and What to Ask For ({YEAR})"
    description = (f"Vegan food in {name}: {n_ok} traditional dishes that are vegan or usually vegan, "
                   f"what to watch for, and a {c['phrase_lang']} phrase card to show your server.")[:158]
    lang = LANG[c["phrase_lang"]]
    roman = f'<span class="roman" lang="{lang}-Latn">{e(c["phrase_roman"])}</span>' if c["phrase_roman"] else ""
    checked = c.get("checked")
    draft = ""
    cards = "\n".join(f"""<li><article class="card"><div class="media">{picture(f"{slug}/{d['name']}", f"{d['name']} ({d['local']})", '(max-width:600px) 100vw, 360px', credit=False)}</div>
<div class="body"><span class="badge {STATUS[d['status']][1]}">{d.get('label') or STATUS[d['status']][0]}</span><h3>{e(d['name'])}</h3><p class="local">{e(d['local'])}</p><p style="margin:4px 0 0">{e(d['note'])}</p></div>{credit_line(f"{slug}/{d['name']}")}</article></li>"""
                      for d in c["dishes"])
    watch = "".join(f"<li>{e(w)}</li>" for w in c["watch"])
    groups = []
    for d in c.get("more_dishes", []):
        if d["group"] not in groups:
            groups.append(d["group"])
    more_html = ""
    if groups:
        more_html = f'<h2 id="more-dishes">More dishes to try in {e(name)}</h2>'
        for g in groups:
            rows = "".join(f"""<li><div><span class="badge {STATUS[d['status']][1]}">{e(d.get('label') or STATUS[d['status']][0])}</span></div><div><h4>{e(d['name'])}</h4><p class="local">{e(d['local'])}</p><p>{e(d['note'])}</p></div></li>"""
                           for d in c["more_dishes"] if d["group"] == g)
            more_html += f'<h3>{e(g)}</h3><ul class="more">{rows}</ul>'
    regions_html = ""
    if c.get("regions"):
        regions_html = f'<h2 id="regions">Region by region</h2><div class="regions">' + "".join(
            f'<div><h3>{e(r["region"])}</h3><p>{e(r["text"])}</p></div>' for r in c["regions"]) + "</div>"
    eat_html = (f'<h2 id="eating-out">Eating out in {e(name)}</h2><ul>' + "".join(f"<li>{e(t)}</li>" for t in c["eating_out"]) + "</ul>") if c.get("eating_out") else ""
    shop_html = (f'<h2 id="shopping">Shopping and self-catering</h2><ul>' + "".join(f"<li>{e(t)}</li>" for t in c["shopping"]) + "</ul>") if c.get("shopping") else ""
    phr_html = ""
    if c.get("phrases"):
        if c["phrase_lang"].startswith("English"):
            phr_html = '<h2 id="phrases">Questions worth asking</h2><ul>' + "".join(f"<li>{e(x['en'])}</li>" for x in c["phrases"]) + "</ul>"
        else:
            rows = "".join(f"""<tr><td>{e(x['en'])}</td><td lang="{lang}">{e(x['local'])}{f'<span class="roman" lang="{lang}-Latn">{e(x["roman"])}</span>' if x.get('roman') else ''}</td></tr>""" for x in c["phrases"])
            phr_html = f'<h2 id="phrases">More useful phrases in {e(c["phrase_lang"])}</h2><table class="phrases"><thead><tr><th>English</th><th>{e(c["phrase_lang"])}</th></tr></thead><tbody>{rows}</tbody></table>'
    faq_html = ""
    if c.get("faqs"):
        faq_html = f'<h2 id="quick-answers">Quick answers</h2><div class="faq">' + "".join(f"<h3>{e(q['q'])}</h3><p>{e(q['a'])}</p>" for q in c["faqs"]) + "</div>"
    prev_c = countries[i - 1] if i > 0 else None
    next_c = countries[i + 1] if i + 1 < len(countries) else None
    pager = ('<nav class="pager" aria-label="More countries">' +
             (f'<a href="{country_path(prev_c)}">&larr; Vegan food in {e(prev_c["name"])}</a>' if prev_c else "<span></span>") +
             (f'<a href="{country_path(next_c)}">Vegan food in {e(next_c["name"])} &rarr;</a>' if next_c else "<span></span>") + "</nav>")
    hero = hero_block(f"{slug}/hero", f"{tname}", f"""<p class="crumbs"><a href="/">Home</a> / <a href="/#countries">Countries</a> / {e(tname)}</p>
<p class="eyebrow" style="color:#bfe3c9">#{c['rank']} most-visited country</p><h1>Vegan Food in {e(name)}</h1>
<p class="lead">How easy: {e(c['ease'])} · Try first: {e(c['first_dish'])}</p>""", short=True)
    body = f"""<article>
<p class="meta" style="margin-top:22px">By <a href="/about/">{AUTHOR}</a> · {('Checked in ' + e(checked) + ' · ') if checked else ''}Updated {TODAY}</p>
{draft}
<p class="lead">{e(c['summary'])}</p>
<div class="glance" aria-label="{e(tname)} at a glance"><div><b>How easy</b>{e(c['ease'])}</div><div><b>Word for vegan</b>{e(c['word'])}</div><div><b>Try first</b>{e(c['first_dish'])}</div></div>
<h2 id="dishes">Traditional dishes in {e(name)} that are vegan or can be</h2>
<ul class="grid">{cards}</ul>
<h2 id="watch">What to watch for in {e(name)}</h2>
<ul class="watch">{watch}</ul>
<h2 id="phrase">How to ask for vegan food in {e(c['phrase_lang'])}</h2>
<p>Show this to your server, or save it to your phone. All 10 countries are on the <a href="/phrase-cards/">phrase cards page</a>.</p>
<p class="phrase" lang="{lang}"><span class="tag">{e(c['phrase_lang'])}</span>{e(c['phrase'])}{roman}</p>
{more_html}
{cta_block(path, slug)}
{regions_html}
{eat_html}
{shop_html}
{phr_html}
{faq_html}
<h2 id="why">Why {e(name)}</h2>
<p>{e(tname)} is the number {c['rank']} most-visited country in the world, with {c['arrivals_m']} million international arrivals in 2024 (UN Tourism).</p>
</article>
{pager}"""
    item_list = {"@type": "ItemList", "name": f"Traditional dishes in {name} that are vegan or can be",
                 "itemListElement": [{"@type": "ListItem", "position": k + 1,
                                      "item": {"@type": "Thing", "name": d["name"], "alternateName": d["local"],
                                               "description": f"{d.get('label') or STATUS[d['status']][0]}. {d['note']}"}}
                                     for k, d in enumerate(all_dishes)]}
    article = {"@context": "https://schema.org", "@type": "Article", "headline": f"Vegan Food in {tname}",
               "description": description, "inLanguage": "en", "dateModified": TODAY, "image": og_image(f"{slug}/hero"),
               "mainEntityOfPage": SITE + path, "author": person(), "publisher": org(),
               "about": {"@type": "Country", "name": c.get("aka") or tname.replace("The ", "")}, "mainEntity": item_list}
    if checked:
        article["datePublished"] = checked
    crumbs = breadcrumb([("Home", "/"), ("Countries", "/#countries"), (tname, path)])
    return path, page(path=path, title=title, description=description, body=body, jsonld=[article, crumbs],
                      indexable=c["verified"], og=og_image(f"{slug}/hero"), hero=hero)


def home(countries):
    cards = "\n".join(f"""<li><a class="card" href="{country_path(c)}"><div class="media">{picture(f"{c['slug']}/hero", cap(c['name']), '(max-width:600px) 100vw, 360px', credit=False)}</div>
<div class="body"><span class="kicker">#{c['rank']} most visited · {e(c['ease'])}</span><span class="name">Vegan food in {e(c['name'])}</span><span class="muted" style="font-size:15px">Try first: {e(c['first_dish'])}</span></div></a></li>""" for c in countries)
    hero = hero_block("home/hero", "Fresh vegetables and chillies at a market", f"""<p class="eyebrow" style="color:#bfe3c9">Vegan food travel guides</p>
<h1>Eat like a local.<br>Stay vegan.</h1>
<p class="lead">The traditional dishes of every country that are already vegan, the ones you can ask for, and exactly how to ask. From over 30 years of travel and {YEARS_VEGAN} years vegan.</p>
<p style="display:flex;gap:12px;flex-wrap:wrap;margin-top:22px"><a class="btn" href="/free-guide/">Get the free phrase cards</a><a class="btn ghost" style="color:#fff!important" href="#countries">Browse countries</a></p>""")
    body = f"""<h2 id="countries">Start with the world's 10 most-visited countries</h2>
<p class="muted">Ranked by international arrivals in 2024 (UN Tourism). Each guide covers the local dishes, what to watch for, and a phrase card.</p>
<ul class="grid">{cards}</ul>
<h2>How it works</h2>
<ol class="steps"><li><b>Find the dishes that are already vegan.</b><br>Every country has traditional food that never had meat in it. Each guide starts there.</li>
<li><b>Know what to watch for.</b><br>Fish sauce in Thailand, dashi in Japan, lard in Mexico. The hidden ingredients, named up front.</li>
<li><b>Show the phrase card.</b><br>One sentence in the local language that tells the kitchen exactly what you eat.</li></ol>
{cta_block("/")}
<div class="founder"><img class="mono" src="/brand/mark.svg" alt="" width="84" height="84"><div><p class="eyebrow">From the founder</p>
<p style="margin:4px 0 8px;font-family:var(--serif);font-size:22px;line-height:1.35">“I've been eating my way around the world for over 30 years. For the last {YEARS_VEGAN}, I've done it vegan. The food is still the best part.”</p>
<p class="meta">{AUTHOR} · <a href="/about/">Read the story</a></p></div></div>"""
    website = {"@context": "https://schema.org", "@type": "WebSite", "@id": SITE + "/#website", "name": BRAND,
               "url": SITE + "/", "description": DESCRIPTOR, "inLanguage": "en", "publisher": {"@id": SITE + "/#org"}}
    return "/", page(path="/", title=f"{BRAND}: Eat Like a Local, Stay Vegan, in Every Country",
                     description="The traditional dishes of every country that are already vegan, what to watch for, and free local-language phrase cards. Start with the 10 most-visited countries.",
                     body=body, jsonld=[website, {"@context": "https://schema.org", **org()}], og=og_image("home/hero"), hero=hero)


def phrase_cards(countries):
    cards = "\n".join(f"""<div><p class="phrase" lang="{LANG[c['phrase_lang']]}"><span class="tag">{e(cap(c['name']))} · {e(c['phrase_lang'])}</span>{e(c['phrase'])}{f'<span class="roman">{e(c["phrase_roman"])}</span>' if c['phrase_roman'] else ''}</p>
<p class="meta">Watch for: {e('; '.join(w.split(' (')[0].split(' in ')[0] for w in c['watch'][:3]))}. <a href="{country_path(c)}">Full guide</a></p></div>""" for c in countries)
    body = f"""<p class="crumbs" style="margin-top:28px"><a href="/">Home</a> / Phrase cards</p>
<h1>Vegan phrase cards for 10 countries</h1>
<p class="lead">One sentence in the local language that tells the kitchen exactly what you don't eat. Show it on your phone or print it. Free to use.</p>
<p class="no-print"><a class="btn" href="/free-guide/">Get the printable pocket pack (PDF)</a></p>
<div class="cards-print">{cards}</div>
{cta_block("/phrase-cards/")}"""
    return "/phrase-cards/", page(path="/phrase-cards/", title="Vegan Phrase Cards in 9 Languages: How to Say 'I'm Vegan' Abroad",
                                  description="How to say 'I am vegan, no meat, fish, eggs or dairy' in French, Spanish, Italian, Turkish, German, Japanese, Greek and more. Free phrase cards for 10 countries.",
                                  body=body, jsonld=[breadcrumb([("Home", "/"), ("Phrase cards", "/phrase-cards/")])])


def free_guide():
    hero = hero_block("home/hero", "Fresh vegetables at a market", """<p class="eyebrow" style="color:#bfe3c9">Free download</p><h1>Never go hungry abroad</h1>
<p class="lead">The pocket phrase-card pack for the world's 10 most-visited countries. Free, instantly.</p>""", short=True)
    body = f"""<section class="cta" style="margin-top:-60px;position:relative;z-index:5">
<div><h2>What's in the pack</h2><p>A printable PDF with one card per country: the vegan sentence in the local language, the three things that most often catch vegans out, and the safest traditional dishes to order.</p>
{signup_form("/free-guide/")}</div>
<div class="pack" aria-hidden="true"><b>Inside</b><ul><li>10 countries, 9 languages</li><li>Romanised Japanese and Greek</li><li>Hidden ingredients to ask about</li><li>Prints on one sheet per country</li></ul></div></section>
<h2>Why people download it</h2>
<ul class="steps"><li><b>It works without wifi.</b><br>Save the PDF to your phone before you fly.</li><li><b>No awkward explaining.</b><br>Show the card and the kitchen knows exactly what you eat.</li><li><b>One short email a week.</b><br>One country, one dish, one phrase. Unsubscribe in one click.</li></ul>"""
    return "/free-guide/", page(path="/free-guide/", title="Free Vegan Phrase-Card Pack for 10 Countries (PDF)",
                                description="Download the free pocket phrase cards: how to order vegan food in 10 countries, what to watch for, and the safest dishes.",
                                body=body, hero=hero)


def thanks():
    body = f"""<div style="padding:60px 0 10px"><p class="eyebrow">You're in</p><h1>Your phrase-card pack is ready</h1>
<p class="lead">Thank you for signing up. Download the pack now and save it to your phone. A copy with the link is also on its way to your inbox within the hour.</p>
<p><a class="btn" href="{PDF_PATH}" download>Download the PDF</a></p>
<p class="muted">The weekly email arrives on Sundays: one country, one dish, one phrase. Every email has a one-click unsubscribe link.</p>
<h2>Where are you going next?</h2><p><a href="/#countries">Browse the country guides</a> or open the <a href="/phrase-cards/">phrase cards</a> on your phone.</p></div>"""
    return "/thanks/", page(path="/thanks/", title="Your free phrase-card pack", description="Download your free vegan phrase-card pack.",
                            body=body, indexable=False, narrow=True)


def unsubscribed():
    body = """<div style="padding:60px 0"><h1>You're unsubscribed</h1><p class="lead">You won't get any more emails from Vegan Food Travel. Safe travels, and good eating.</p>
<p>Changed your mind? <a href="/free-guide/">Sign up again</a>.</p></div>"""
    return "/unsubscribed/", page(path="/unsubscribed/", title="Unsubscribed", description="You have been unsubscribed.",
                                  body=body, indexable=False, narrow=True)


def about():
    body = f"""<div class="prose" style="padding-top:40px"><p class="crumbs"><a href="/">Home</a> / About</p>
<h1>I've been eating my way around the world for over 30 years. For the last {YEARS_VEGAN}, I've done it vegan.</h1>
<p class="lead">I'm {AUTHOR}, a New Zealander and a foodie. Travel has been part of my working life from the start, and food has always been my favourite part of it.</p>
<h2>How I got here</h2>
<p>I started travelling with the Royal New Zealand Navy. Later I worked on cruise ships and superyachts, and since then I've kept travelling for work and on holiday. Over 30 years that has added up to dozens of countries, and in every one of them I've gone looking for what the locals eat.</p>
<p>When I went vegan in {VEGAN_SINCE}, people assumed that part of travel was over for me. It wasn't. In most countries, some of the best traditional dishes are already vegan. Others are one simple request away. You just need to know which ones, and how to ask.</p>
<h2>What this site is for</h2>
<p>{BRAND} closes the gap between what vegan travellers worry about and what is actually on the table. Each guide covers one country:</p>
<ul><li>the dishes that are vegan by tradition</li>
<li>the ones you can ask for vegan, and exactly what to say</li>
<li>the hidden ingredients to watch for, like fish stock or lard</li>
<li>a phrase card in the local language to show your server</li></ul>
<p>No lectures, and no sad side salads. Just the local food, eaten the local way.</p>
<h2>My promises to you</h2>
<ul><li>I've been to every country I cover and eaten the food there.</li>
<li>Nobody pays to be included. Some links may earn a commission; they never decide what I recommend.</li>
<li>If something has changed, <a href="/contact/">tell me</a>. Corrections are dated on the page.</li></ul></div>
{cta_block("/about/")}"""
    p = {"@context": "https://schema.org", "@type": "AboutPage", "url": SITE + "/about/", "mainEntity": person(), "publisher": org()}
    return "/about/", page(path="/about/", title=f"About {BRAND}: Over 30 Years of Travel, {YEARS_VEGAN} Years Vegan",
                           description=f"{AUTHOR} has travelled to dozens of countries for over 30 years, with the Navy, on cruise ships and superyachts, and has been vegan since {VEGAN_SINCE}.",
                           body=body, jsonld=[p], narrow=True)


def contact():
    body = f"""<div class="prose" style="padding-top:40px"><h1>Contact</h1>
<p class="lead">Spotted something that has changed, or want a country covered next? Email me.</p>
<p style="font-size:22px"><a href="mailto:{EMAIL}">{EMAIL}</a></p>
<p class="muted">I read every message. Corrections to a guide are dated on the page.</p></div>"""
    return "/contact/", page(path="/contact/", title=f"Contact {BRAND}", description=f"Email {BRAND} at {EMAIL}.", body=body, narrow=True)


def privacy():
    body = f"""<div class="prose" style="padding-top:40px"><h1>Privacy</h1><p class="meta">Last updated {TODAY}</p>
<p>{BRAND} collects as little as possible. This page explains what, why, and your choices.</p>
<h2>If you sign up</h2><ul><li>I store your email address, the page you signed up on, the date, the country your connection came from (from Cloudflare), and the wording you agreed to.</li>
<li>I use it only to send what you asked for: the phrase-card pack and the weekly email. I never sell or share your address.</li>
<li>Every email has a one-click unsubscribe link. You can also email <a href="mailto:{EMAIL}">{EMAIL}</a> to have your details deleted.</li>
<li>Signups are stored in a Cloudflare D1 database. Emails are sent through Resend, an email delivery provider that processes your address only to deliver them.</li></ul>
<h2>Analytics</h2><p>The site uses Cloudflare Web Analytics, which counts visits without cookies and without tracking you across sites.</p>
<h2>Cookies</h2><p>The site sets no cookies.</p>
<h2>Your rights</h2><p>You can ask to see, correct or delete your information at any time by emailing <a href="mailto:{EMAIL}">{EMAIL}</a>. If you are in New Zealand, the Privacy Act 2020 applies; in the UK or EU, the GDPR. You can complain to your local privacy regulator.</p></div>"""
    return "/privacy/", page(path="/privacy/", title="Privacy Policy", description=f"How {BRAND} handles your information.", body=body, narrow=True)


def terms():
    body = f"""<div class="prose" style="padding-top:40px"><h1>Terms and disclosure</h1><p class="meta">Last updated {TODAY}</p>
<h2>Information, not a guarantee</h2><p>Recipes change between kitchens. The guides say what is traditional and what to ask about, but always confirm ingredients where you eat, especially if you have an allergy.</p>
<h2>Independence</h2><p>Nobody pays to be included or to be ranked. Some links may be affiliate links, which earn a small commission at no cost to you. They are marked, and they never decide what is recommended.</p>
<h2>Photos</h2><p>Photos are free-licensed from Wikimedia Commons under the licences shown beside each one, resized for the web. See <a href="/photo-credits/">photo credits</a>.</p>
<h2>Copyright</h2><p>Text © {YEAR} {BRAND}. Phrase cards may be printed and shared for personal use.</p>
<h2>Contact</h2><p><a href="mailto:{EMAIL}">{EMAIL}</a></p></div>"""
    return "/terms/", page(path="/terms/", title="Terms and Disclosure", description=f"Terms of use, independence and affiliate disclosure for {BRAND}.", body=body, narrow=True)


def photo_credits():
    rows = []
    for key, c in sorted(CREDITS.items()):
        where = key.replace("/", " · ").replace("home", "Home page")
        lic = f'<a href="{e(c["license_url"])}" rel="license nofollow">{e(c["license"])}</a>' if c.get("license_url") else e(c["license"])
        rows.append(f'<tr><td>{e(cap(where))}</td><td><a href="{e(c["page"])}" rel="nofollow">{e(c["author"])}</a></td><td>{lic}</td></tr>')
    table = ("<table style='width:100%;border-collapse:collapse;font-size:14px'><thead><tr><th align=left>Where</th><th align=left>Photographer</th><th align=left>Licence</th></tr></thead><tbody>"
             + "".join(rows) + "</tbody></table>") if rows else "<p>Photo credits are being prepared.</p>"
    body = f"""<div class="prose" style="padding-top:40px"><h1>Photo credits</h1><p>All photos come from Wikimedia Commons under free licences and have been resized for the web. Thank you to every photographer.</p>{table}</div>"""
    return "/photo-credits/", page(path="/photo-credits/", title="Photo Credits", description="Credits and licences for photos used on Vegan Food Travel.",
                                   body=body, indexable=False, narrow=True)


ROBOTS = f"""# {BRAND}: search engines and AI search crawlers are welcome.
User-agent: *
Allow: /
Disallow: /api/
Disallow: /thanks/

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

HEADERS = """/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=()
  Content-Security-Policy: default-src 'self'; style-src 'unsafe-inline'; img-src 'self' data:; script-src 'self' 'unsafe-inline' https://static.cloudflareinsights.com; connect-src 'self' https://cloudflareinsights.com; base-uri 'self'; form-action 'self'; frame-ancestors 'none'
/img/*
  Cache-Control: public, max-age=31536000, immutable
/brand/*
  Cache-Control: public, max-age=604800
"""


def build():
    countries = sorted(json.loads((ROOT / "data/countries.json").read_text()), key=lambda c: c["rank"])
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "static", OUT)
    pages = [home(countries), about(), phrase_cards(countries), free_guide(), thanks(), unsubscribed(),
             contact(), privacy(), terms(), photo_credits()] + [country_page(c, countries, i) for i, c in enumerate(countries)]
    for path, content in pages:
        target = OUT / "index.html" if path == "/" else OUT / path.strip("/") / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
    indexable = ["/", "/about/", "/phrase-cards/", "/free-guide/", "/contact/", "/privacy/", "/terms/"] + \
                [country_path(c) for c in countries if c["verified"]]
    sm = "\n".join(f"  <url><loc>{SITE}{p}</loc><lastmod>{TODAY}</lastmod></url>" for p in indexable)
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sm}\n</urlset>\n')
    (OUT / "robots.txt").write_text(ROBOTS)
    (OUT / "_headers").write_text(HEADERS)
    (OUT / f"{INDEXNOW_KEY}.txt").write_text(INDEXNOW_KEY)
    (OUT / "404.html").write_text(page(path="/404", title="Page not found", description="Page not found.",
                                       body='<div style="padding:80px 0"><h1>Page not found</h1><p><a class="btn" href="/#countries">See all countries</a></p></div>',
                                       indexable=False, narrow=True))
    n_img = sum(1 for _ in (OUT / "img").glob("*-960.webp")) if (OUT / "img").exists() else 0
    print(f"Built {len(pages)} pages; {len(indexable)} indexable; {n_img} photos; {sum(not c['verified'] for c in countries)} draft guides hidden.")


if __name__ == "__main__":
    build()
