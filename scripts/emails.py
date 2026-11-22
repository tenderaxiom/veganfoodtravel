#!/usr/bin/env python3
"""Generate Vegan Food Travel emails as JSON {subject, html, text, headers} for one recipient.

  python scripts/emails.py welcome <step 1-4> <token>
  python scripts/emails.py weekly <iso-week-number> <token>

The token is the subscriber's unsubscribe token from the D1 subscribers table.
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://veganfoodtravel.com"
ADDRESS = "21 Queen Street, Auckland CBD, Auckland 1010, New Zealand"
e = html.escape
STATUS = {"vegan": "Vegan by tradition", "usually": "Usually vegan: check", "ask": "Ask for it vegan", "no": "Not vegan as standard"}


def countries():
    return sorted(json.loads((ROOT / "data/countries.json").read_text()), key=lambda c: (c.get("rank") or 99, c["name"]))


def cap(s):
    return s[0].upper() + s[1:]


def wrap(subject, preheader, blocks, token):
    unsub = f"{SITE}/api/unsubscribe?t={token}"
    body_html = "".join(blocks)
    html_doc = f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>{e(subject)}</title></head>
<body style="margin:0;background:#fbfaf6;font-family:-apple-system,'Segoe UI',Roboto,Arial,sans-serif;color:#1d2a22">
<span style="display:none;max-height:0;overflow:hidden">{e(preheader)}</span>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#fbfaf6"><tr><td align="center" style="padding:24px 12px">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;background:#ffffff;border-radius:16px;overflow:hidden">
<tr><td style="background:#2f6b45;padding:18px 28px"><a href="{SITE}" style="color:#ffffff;text-decoration:none;font-family:Georgia,serif;font-size:20px;font-weight:bold">Vegan <span style="color:#bfe3c9">Food</span> Travel</a>
<div style="color:#d9e8de;font-size:11px;letter-spacing:2px;margin-top:2px">EAT LIKE A LOCAL · STAY VEGAN</div></td></tr>
<tr><td style="padding:28px;font-size:16px;line-height:1.6">{body_html}</td></tr>
<tr><td style="padding:18px 28px;background:#f3f1ea;font-size:12px;line-height:1.5;color:#5b6b60">
You're getting this because you signed up at veganfoodtravel.com. <a href="{unsub}" style="color:#5b6b60">Unsubscribe in one click</a>.<br>
Vegan Food Travel · {ADDRESS} · <a href="mailto:hello@veganfoodtravel.com" style="color:#5b6b60">hello@veganfoodtravel.com</a></td></tr>
</table></td></tr></table></body></html>"""
    text = "\n\n".join(b for b in TEXT_BLOCKS) + f"\n\n--\nUnsubscribe: {unsub}\nVegan Food Travel, {ADDRESS}"
    return {"subject": subject, "html": html_doc, "text": text,
            "headers": {"List-Unsubscribe": f"<{unsub}>, <mailto:hello@veganfoodtravel.com?subject=unsubscribe>",
                        "List-Unsubscribe-Post": "List-Unsubscribe=One-Click"}}


TEXT_BLOCKS = []


def p(t, style=""):
    TEXT_BLOCKS.append(html.unescape(re.sub(r"<[^>]+>", "", t.replace("<br>", "\n"))))
    return f'<p style="margin:0 0 16px;{style}">{t}</p>'


def btn(label, url):
    TEXT_BLOCKS.append(f"{label}: {url}")
    return (f'<p style="margin:22px 0"><a href="{url}" style="background:#2f6b45;color:#ffffff;text-decoration:none;'
            f'font-weight:bold;padding:12px 22px;border-radius:999px;display:inline-block">{e(label)}</a></p>')


def card(phrase, lang_label, roman=""):
    TEXT_BLOCKS.append(f"[{lang_label}] {phrase}" + (f"\n({roman})" if roman else ""))
    r = f'<div style="color:#5b6b60;font-size:13px;margin-top:8px">{e(roman)}</div>' if roman else ""
    return (f'<div style="border:2px dashed #2f6b45;border-radius:14px;padding:16px 18px;margin:8px 0 20px;background:#fffdf7">'
            f'<div style="font-size:11px;letter-spacing:1.5px;color:#2f6b45;font-weight:bold">{e(lang_label.upper())}</div>'
            f'<div style="font-size:18px;margin-top:6px">{e(phrase)}</div>{r}</div>')


def welcome(step, token):
    cs = countries()
    by = {c["slug"]: c for c in cs}
    if step == 1:
        s, pre = "Your vegan phrase cards are here", "Save the PDF to your phone before you fly."
        blocks = [p("Hi,"),
                  p(f"Here's your free pocket pack: the vegan sentence in the local language for {len(countries())} countries, what to watch for, and the safest dishes to order."),
                  btn("Download the phrase cards (PDF)", f"{SITE}/free/vegan-phrase-cards.pdf"),
                  p("<b>One tip:</b> save it to your phone now, so it works without wifi when you land."),
                  p("Where are you heading next? Just hit reply and tell me. I read every message, and it decides which countries I cover next."),
                  p("Richard<br>Vegan Food Travel")]
    elif step == 2:
        j = by["japan"]
        s, pre = "The fish stock hiding in Japanese food", "And the other hidden ingredients worth asking about."
        blocks = [p("Hi,"),
                  p("What catches vegans out abroad usually isn't meat. It's the stock and the fat. In Japan, <b>dashi</b>, a stock usually made from bonito fish, is in most soups, sauces and noodle broths, including miso soup."),
                  p("So in Japan, add one line when you order:"),
                  card(j["phrase"], "Japanese", j["phrase_roman"]),
                  p("Every country has its own version: fish sauce in Thailand, lard in Mexican beans, Maldive fish in Sri Lankan sambol, Parmesan grated over Italian pasta. Each country guide names them up front."),
                  btn("Browse the country guides", f"{SITE}/#countries"),
                  p("Richard")]
    elif step == 3:
        s, pre = "How I eat vegan anywhere: 3 questions", "The three questions I ask in every country."
        blocks = [p("Hi,"),
                  p("After years of eating vegan abroad, ordering comes down to three questions:"),
                  p("<b>1. What is already vegan here?</b> Most food cultures have dishes that never had meat in them: Greek fasting food, Buddhist temple cooking, Italian peasant dishes. Start there."),
                  p("<b>2. What's in the stock or the fat?</b> Butter, lard, fish sauce, meat stock. These are the hidden ingredients, not the obvious ones."),
                  p("<b>3. Can they leave one thing off?</b> Cheese on top, egg on the side, yogurt in the sauce. Asking for one change works far better than asking for a whole new dish."),
                  p("I've written the full method up, with the word for vegan in 14 languages and the hidden ingredients to ask about."),
                  btn("How to ask for vegan food anywhere", f"{SITE}/how-to-ask-for-vegan-food/"),
                  p("Flying soon? Order the VGML meal at least a day ahead. More here: " + SITE + "/vegan-meals-on-flights/"),
                  p("Richard")]
    else:
        s, pre = "Every Sunday: one country, one dish, one phrase", "What to expect from here."
        blocks = [p("Hi,"),
                  p("From this Sunday, you'll get one short email a week: one country, one traditional dish that's vegan or can be, and one phrase to order it. Two minutes to read, useful the next time you travel."),
                  p("If you'd rather not, the unsubscribe link is at the bottom of every email. No hard feelings."),
                  btn("Browse all the country guides", f"{SITE}/#countries"),
                  p("Richard")]
    return wrap(s, pre, blocks, token)


def weekly(week, token):
    cs = countries()
    c = cs[week % len(cs)]
    good = [d for d in c["dishes"] if d["status"] in ("vegan", "usually")]
    d = good[(week // len(cs)) % len(good)]
    name = cap(c["name"])
    s = f"Vegan in {c.get('short', c['name']).replace('the ', '')}: {d['name']}"
    pre = f"One dish, one phrase, one thing to watch for in {name}."
    blocks = [p(f"<b>This week: {e(name)}</b>", "font-family:Georgia,serif;font-size:22px"),
              p(e(c["summary"])),
              p(f"<b>The dish: {e(d['name'])}</b> <i>({e(d['local'])})</i><br>{e(d.get('label') or STATUS[d['status']])}. {e(d['note'])}"),
              p("<b>The phrase:</b>"),
              card(c["phrase"], c["phrase_lang"], c["phrase_roman"]),
              p(f"<b>Watch for:</b> {e(c['watch'][0])}."),
              btn(f"Read the full {name} guide", f"{SITE}/vegan-food-in-{c['slug']}/"),
              p("Recipes vary between kitchens, so always confirm ingredients where you eat.", "font-size:13px;color:#5b6b60"),
              p("Hit reply and tell me where you're travelling next.<br>Richard")]
    return wrap(s, pre, blocks, token)


if __name__ == "__main__":
    kind, n, tok = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    out = welcome(n, tok) if kind == "welcome" else weekly(n, tok)
    print(json.dumps(out, ensure_ascii=False))
