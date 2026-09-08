# -*- coding: utf-8 -*-
"""空っぽに見える楽天ページが、どこからデータを取っているかを探す。"""
import io, re, sys, collections

sys.stdout.reconfigure(encoding="utf-8")
h = io.open("tmp/rk_raw.html", encoding="utf-8").read()

print("=== 通信しそうな記述 ===")
seen = set()
for p in [r"fetch\([^)]{0,120}",
          r"\.ajax\([^)]{0,120}",
          r"XMLHttpRequest",
          r"/api/[\w/.-]{0,80}",
          r'data-[a-z-]*url="[^"]{0,120}"',
          r"https://[a-z0-9.-]*rakuten[^\"'\s<>]{0,90}"]:
    for m in re.findall(p, h):
        if m in seen:
            continue
        seen.add(m)
        print("  " + m[:120])

print()
print("=== data-* 属性の種類 ===")
c = collections.Counter(re.findall(r"(data-[a-z-]+)=", h))
for k, v in c.most_common(25):
    print("  %-26s %d" % (k, v))

print()
print("=== 外部scriptのsrc ===")
for s in sorted(set(re.findall(r'<script[^>]+src="([^"]+)"', h)))[:25]:
    print("  " + s[:120])

print()
print("=== 本文らしき見出し（h1/h2）===")
for m in re.findall(r"<h[12][^>]*>(.*?)</h[12]>", h, re.S)[:12]:
    t = re.sub(r"<[^>]+>", " ", m)
    t = re.sub(r"\s+", " ", t).strip()
    if t:
        print("  " + t[:80])
