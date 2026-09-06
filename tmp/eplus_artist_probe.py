# -*- coding: utf-8 -*-
"""e+の詳細ページから出演者情報がどこに入っているか調べる（3件だけ試す）"""
import re, sys, json, urllib.request
sys.stdout.reconfigure(encoding="utf-8")

URLS = [
 ("6979", "https://eplus.jp/sf/detail/4090460001-P0030001P021001"),
]
h = open("index.html", encoding="utf-8").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))
pick = {e["id"]: e for e in EVENTS}
for eid in (6979, 6953, 6968):
    e = pick[eid]
    url = (e.get("links") or {}).get("eplus")
    print("=== id=%d %s" % (eid, url))
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    for ld in re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', html, re.S):
        try:
            d = json.loads(ld)
        except Exception:
            continue
        print("  LD keys:", list(d.keys()) if isinstance(d, dict) else type(d))
        if isinstance(d, dict):
            print("   name:", d.get("name"))
            print("   performer:", json.dumps(d.get("performer"), ensure_ascii=False)[:300])
    for pat in [r'出演[^<]{0,10}</[^>]+>\s*<[^>]+>(.{0,200}?)</', r'class="[^"]*performer[^"]*"[^>]*>(.{0,200}?)<']:
        mm = re.search(pat, html, re.S)
        if mm:
            print("  HTML出演:", re.sub(r'\s+', ' ', mm.group(1))[:200])
