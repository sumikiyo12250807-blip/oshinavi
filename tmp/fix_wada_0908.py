# -*- coding: utf-8 -*-
"""id4612 和田唱の「看板と中身の食い違い」を直す。

見つかった状態（2026-09-08）:
  エントリ = 会場「cafe Room+」・公演日 2026-10-17・県「大阪」
  持っている枠 = 「一般発売（北海道 10/12公演）〜9/24」の1本だけ
  links.pia = eventCd=2632972 → ぴあで無効化されている
ぴあの実物:
  和田唱 10/12 SPiCE(北海道)  eventCd=2633419  ← この枠の正体
  和田唱（TRICERATOPS）10/16 ROOMS(福岡) eventCd=2633160 ← 未登録（別エントリで足す）

🚨大阪 cafe Room+ 10/17 はぴあに無い＝**この看板の裏が取れない**ので、
   枠の実体（北海道10/12）に合わせて直す。推測で大阪の枠を作らない。
🚨値だけの書き換えなので**行ベースのピンポイント置換**（配列を作り直さない）。
"""
import io, json, re

PATH = "index.html"
TARGET = 4612
NEW = {
    "date": "2026-10-12",
    "dateLabel": "2026年10月12日(月) 北海道 SPiCE",
    "venue": "SPiCE",
    "prefecture": "北海道",
}
NEW_PIA = "https://t.pia.jp/pia/event/event.do?eventCd=2633419"

raw = io.open(PATH, encoding="utf-8", newline="").read()
lines = raw.split("\r\n")

cur = None
hits = []
in_links = False
for i, ln in enumerate(lines):
    m = re.match(r'\s*"id":\s*(\d+),\s*$', ln)
    if m:
        cur = int(m.group(1))
        in_links = False
        continue
    if cur != TARGET:
        continue
    if re.match(r'\s*"links":\s*\{', ln):
        in_links = True
        continue
    if in_links and re.match(r"\s*\},\s*$", ln):
        in_links = False
        continue
    if in_links:
        m4 = re.match(r'(\s*"pia":\s*)(".*?"|null)(,?)\s*$', ln)
        if m4:
            lines[i] = m4.group(1) + json.dumps(NEW_PIA, ensure_ascii=False) + m4.group(3)
            hits.append(("links.pia", i, ln.strip(), lines[i].strip()))
        continue
    for k, v in NEW.items():
        m2 = re.match(r'(    "%s":\s*)(".*?")(,?)\s*$' % k, ln)
        if m2:
            lines[i] = m2.group(1) + json.dumps(v, ensure_ascii=False) + m2.group(3)
            hits.append((k, i, ln.strip(), lines[i].strip()))
            break

assert len(hits) == 5, "置換対象が5行でない: %d %s" % (len(hits), [h[0] for h in hits])
io.open(PATH, "w", encoding="utf-8", newline="").write("\r\n".join(lines))

o = io.open("tmp/fix_wada_0908.txt", "w", encoding="utf-8")
for k, i, before, after in hits:
    o.write("%s (行%d)\n  前: %s\n  後: %s\n" % (k, i + 1, before, after))
o.close()

s2 = io.open(PATH, encoding="utf-8", newline="").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", s2, re.S).group(1))
e = [x for x in EV if x["id"] == TARGET][0]
b = open(PATH, "rb").read()
crlf = b.count(b"\r\n")
print("date=%s venue=%s pref=%s pia_ok=%s EVENTS=%d CRLF=%d bareLF=%d CRCRLF=%d"
      % (e["date"], e["venue"], e["prefecture"], (e.get("links") or {}).get("pia") == NEW_PIA,
         len(EV), crlf, b.count(b"\n") - crlf, b.count(b"\r\r\n")))
