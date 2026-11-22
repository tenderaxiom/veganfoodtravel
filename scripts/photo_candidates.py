#!/usr/bin/env python3
"""Search Wikimedia Commons for candidate photos and make labelled contact sheets.

Reads data/photo_queries.json {"key": "search words"}; for each key, finds up to 6 free-licensed
JPEG/PNG photos at least 1200px wide and draws them in one row. Rows are grouped 4 keys per sheet
in candidates/sheet-NN.png; candidates/index.json maps key -> [file names] in display order.
A person then picks the right photo for each key and adds it to data/photos.json.
"""
import io, json, re, sys, time, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
UA = "VeganFoodTravelBot/1.0 (https://veganfoodtravel.com; hello@veganfoodtravel.com)"
FREE = re.compile(r"^(CC0|CC BY(-SA)? [0-9.]+|Public domain|PD.*)$", re.I)
OUT = ROOT / "candidates"
TW, TH, N = 300, 220, 6


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for a in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except Exception:
            time.sleep(3 * (a + 1))
    return None


def search(q):
    params = {"action": "query", "format": "json", "generator": "search", "gsrnamespace": "6",
              "gsrsearch": q + " filetype:bitmap", "gsrlimit": "25", "prop": "imageinfo",
              "iiprop": "url|size|extmetadata|mime", "iiurlwidth": str(TW * 2)}
    raw = get("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params))
    if not raw:
        return []
    pages = sorted(json.loads(raw).get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 99))
    out = []
    for p in pages:
        ii = (p.get("imageinfo") or [None])[0]
        if not ii or ii.get("mime") not in ("image/jpeg", "image/png") or ii.get("width", 0) < 1200:
            continue
        lic = ii.get("extmetadata", {}).get("LicenseShortName", {}).get("value", "")
        if not FREE.match(lic.strip()):
            continue
        out.append((p["title"][5:], ii["thumburl"]))
        if len(out) == N:
            break
    return out


def main():
    queries = json.loads((ROOT / "data/photo_queries.json").read_text())
    OUT.mkdir(exist_ok=True)
    for f in OUT.glob("*"):
        f.unlink()
    font = ImageFont.load_default(size=16)
    index, rows = {}, []
    for key, q in queries.items():
        found = search(q)
        index[key] = [f for f, _ in found]
        row = Image.new("RGB", (TW * N, TH + 34), "white")
        d = ImageDraw.Draw(row)
        d.text((6, 4), f"{key}  [{q}]", fill="black", font=font)
        for i, (fname, url) in enumerate(found):
            data = get(url)
            if not data:
                continue
            im = Image.open(io.BytesIO(data)).convert("RGB")
            im.thumbnail((TW - 6, TH - 6))
            row.paste(im, (i * TW + 3, 30))
            d.rectangle([i * TW + 3, 30, i * TW + 30, 52], fill="black")
            d.text((i * TW + 8, 32), str(i + 1), fill="yellow", font=font)
        rows.append(row)
        print(key, len(found), flush=True)
    for s in range(0, len(rows), 4):
        chunk = rows[s:s + 4]
        sheet = Image.new("RGB", (TW * N, sum(r.height for r in chunk)), "white")
        y = 0
        for r in chunk:
            sheet.paste(r, (0, y)); y += r.height
        sheet.save(OUT / f"sheet-{s // 4 + 1:02d}.png")
    (OUT / "index.json").write_text(json.dumps(index, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
