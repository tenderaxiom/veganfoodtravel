#!/usr/bin/env python3
"""Download the Wikimedia Commons photos listed in data/photos.json.

For each photo: look up its licence and author, download a 1600px version, and save
compressed WebP files at 1600, 960 and 480 pixels wide in static/img/. Credits go to
data/photo_credits.json so every page can attribute the photographer and licence.
Runs in GitHub Actions (the build server has internet access); skips photos already done.
"""
import io
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
UA = "VeganFoodTravelBot/1.0 (https://veganfoodtravel.com; hello@veganfoodtravel.com)"
OUT = ROOT / "static" / "img"
CREDITS = ROOT / "data" / "photo_credits.json"
WIDTHS = (1600, 960, 480)
FREE = re.compile(r"^(CC0|CC BY(-SA)? [0-9.]+|Public domain|PD.*)$", re.I)


def slug(key):
    s = key.lower().replace("/", "--")
    s = re.sub(r"[^a-z0-9-]+", "-", s.encode("ascii", "ignore").decode())
    return re.sub(r"-+", "-", s).strip("-")


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except Exception:
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"download failed: {url}")


def info(files):
    q = urllib.parse.urlencode({
        "action": "query", "format": "json", "prop": "imageinfo",
        "iiprop": "url|extmetadata", "iiurlwidth": "1600",
        "titles": "|".join("File:" + f for f in files)})
    data = json.loads(get("https://commons.wikimedia.org/w/api.php?" + q))
    norm = {n["to"]: n["from"] for n in data["query"].get("normalized", [])}
    out = {}
    for p in data["query"]["pages"].values():
        title = norm.get(p["title"], p["title"])[5:]
        ii = (p.get("imageinfo") or [None])[0]
        if not ii:
            continue
        m = ii.get("extmetadata", {})
        artist = re.sub(r"<[^>]+>", "", m.get("Artist", {}).get("value", "")).strip()
        out[title] = {
            "src": ii.get("thumburl") or ii["url"],
            "page": ii["descriptionurl"],
            "license": m.get("LicenseShortName", {}).get("value", ""),
            "license_url": m.get("LicenseUrl", {}).get("value", ""),
            "author": re.sub(r"\s+", " ", artist)[:120] or "Unknown author",
        }
    return out


def main():
    photos = {k: v for k, v in json.loads((ROOT / "data/photos.json").read_text()).items() if not k.startswith("_")}
    credits = json.loads(CREDITS.read_text()) if CREDITS.exists() else {}
    OUT.mkdir(parents=True, exist_ok=True)
    todo = [k for k, f in photos.items()
            if credits.get(k, {}).get("file") != f or not (OUT / f"{slug(k)}-960.webp").exists()]
    names = sorted({photos[k] for k in todo})
    meta = {}
    for i in range(0, len(names), 40):
        meta.update(info(names[i:i + 40]))
    for key in todo:
        f = photos[key]
        m = meta.get(f) or meta.get(f.replace("_", " "))
        if not m:
            print("MISSING", key, f)
            continue
        if not FREE.match(m["license"]):
            print("SKIPPED (licence)", key, m["license"])
            continue
        img = ImageOps.exif_transpose(Image.open(io.BytesIO(get(m["src"])))).convert("RGB")
        s = slug(key)
        for w in WIDTHS:
            im = img if img.width <= w else img.resize((w, round(img.height * w / img.width)), Image.LANCZOS)
            im.save(OUT / f"{s}-{w}.webp", "WEBP", quality=78, method=6)
        credits[key] = {"file": f, "slug": s, "w": img.width, "h": img.height, **{k: m[k] for k in ("page", "license", "license_url", "author")}}
        print("OK", key, m["license"])
        time.sleep(0.5)
    for k in list(credits):
        if k not in photos:
            credits.pop(k)
    CREDITS.write_text(json.dumps(credits, ensure_ascii=False, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
