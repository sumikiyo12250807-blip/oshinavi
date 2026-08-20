# -*- coding: utf-8 -*-
"""興行トップHTMLから公演ごとの detail URL を素直に拾う（925 忘れらんねえよ 大阪8/11 用）。"""
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

url = sys.argv[1] if len(sys.argv) > 1 else "https://eplus.jp/sf/detail/0753900001"
h = urllib.request.urlopen(
    urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60
).read().decode("utf-8", "replace")
print("len=%d" % len(h))

pats = [
    r'/sf/detail/[0-9A-Za-z\-]{10,}',
]
seen = []
for p in pats:
    for m in re.findall(p, h):
        if m not in seen:
            seen.append(m)
print("--- detail風URL %d件 ---" % len(seen))
for s in seen[:40]:
    print("  https://eplus.jp" + s)

print("--- option value ---")
for m in re.findall(r'<option[^>]*value="([^"]*)"[^>]*>(.*?)</option>', h, re.S)[:40]:
    v = m[0]
    t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m[1])).strip()
    if t and re.search(r"\d{4}/\d", t):
        print("  value=%s  %s" % (v[:60], t))
