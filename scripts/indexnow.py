#!/usr/bin/env python3
"""Tell IndexNow search engines (Bing, Yandex, Seznam, Naver and others) which pages changed.

Runs after each push to main. Submits every URL in the built sitemap; only indexable
(checked) pages are in the sitemap, so drafts are never submitted.
"""
import json
import re
import urllib.request
from pathlib import Path

import importlib.util

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("build", ROOT / "build.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

urls = re.findall(r"<loc>(.*?)</loc>", (ROOT / "dist/sitemap.xml").read_text())
payload = {
    "host": "veganfoodtravel.com",
    "key": build.INDEXNOW_KEY,
    "keyLocation": f"{build.SITE}/{build.INDEXNOW_KEY}.txt",
    "urlList": urls,
}
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=json.dumps(payload).encode(),
                             headers={"Content-Type": "application/json; charset=utf-8"})
with urllib.request.urlopen(req, timeout=30) as r:
    print("IndexNow", r.status, len(urls), "URLs")
