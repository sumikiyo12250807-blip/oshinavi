# -*- coding: utf-8 -*-
"""読めなかった楽天ページを1枚だけ開いて、何が書いてあるのかを人が読める形で出す。"""
import io, re, sys, urllib.request, html

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
url = sys.argv[1] if len(sys.argv) > 1 else "https://ticket.rakuten.co.jp/music/jpop/idle/rtzzz49/"

h = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode("utf-8", "replace")
io.open("tmp/rk_raw.html", "w", encoding="utf-8").write(h)

o = io.open("tmp/rk_peek_0908.txt", "w", encoding="utf-8")
o.write("URL: %s\nHTML長: %d\n\n" % (url, len(h)))

o.write("=== <title> と og ===\n")
for pat in [r"<title>(.*?)</title>", r'property="og:title" content="([^"]*)"',
            r'property="og:url" content="([^"]*)"', r'name="description" content="([^"]*)"']:
    m = re.search(pat, h, re.S)
    o.write("  %s\n" % (html.unescape(m.group(1))[:120] if m else "(無し)"))

o.write("\n=== 「販売期間」のまわり（3か所まで）===\n")
for m in list(re.finditer(r"販売期間", h))[:3]:
    seg = h[max(0, m.start() - 400): m.start() + 700]
    seg = re.sub(r"<script.*?</script>", "", seg, flags=re.S)
    seg = re.sub(r"<[^>]+>", " ", seg)
    seg = re.sub(r"\s+", " ", html.unescape(seg)).strip()
    o.write("  ...%s...\n\n" % seg[:600])

o.write("=== class に performance / event / sales を含むもの（上位20）===\n")
import collections
cls = collections.Counter(re.findall(r'class="([^"]{0,60})"', h) + re.findall(r"class='([^']{0,60})'", h))
for c, n in cls.most_common(200):
    if re.search(r"perform|event|sale|ticket|date|venue|area", c, re.I):
        o.write("  %-52s %d\n" % (c, n))

o.write("\n=== var で始まるJSの変数名 ===\n")
for v in sorted(set(re.findall(r"var\s+([A-Za-z_][\w]*)\s*=", h)))[:40]:
    o.write("  %s\n" % v)
o.close()
print("wrote tmp/rk_peek_0908.txt / tmp/rk_raw.html")
