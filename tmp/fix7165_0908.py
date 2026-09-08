# -*- coding: utf-8 -*-
"""id7165 博多・天神落語まつり の date / dateLabel を事実（千秋楽11/3）に直す。
   🚨配列を作り直さない＝該当する行だけを置換する（feedback_index_html_crlf_preserve）。"""
import io, json, re

PATH = "index.html"
TARGET = 7165
NEW_DATE = "2026-11-03"
NEW_LABEL = "2026年10月30日(金)〜2026年11月3日(火) 福岡"

raw = io.open(PATH, encoding="utf-8", newline="").read()
lines = raw.split("\r\n")

cur = None
hits = []
for i, ln in enumerate(lines):
    m = re.match(r'\s*"id":\s*(\d+),\s*$', ln)
    if m:
        cur = int(m.group(1))
        continue
    if cur != TARGET:
        continue
    # 🚨エントリ直下は4スペース、チケットの中は8スペース。4スペースだけを狙う
    m2 = re.match(r'(    "date":\s*)(".*?")(,?)\s*$', ln)
    if m2:
        lines[i] = m2.group(1) + json.dumps(NEW_DATE, ensure_ascii=False) + m2.group(3)
        hits.append(("date", i, ln.strip(), lines[i].strip()))
        continue
    m3 = re.match(r'(    "dateLabel":\s*)(".*?")(,?)\s*$', ln)
    if m3:
        lines[i] = m3.group(1) + json.dumps(NEW_LABEL, ensure_ascii=False) + m3.group(3)
        hits.append(("dateLabel", i, ln.strip(), lines[i].strip()))

assert len(hits) == 2, "置換対象が2行でない: %d" % len(hits)

io.open(PATH, "w", encoding="utf-8", newline="").write("\r\n".join(lines))

o = io.open("tmp/fix7165_0908.txt", "w", encoding="utf-8")
for k, i, before, after in hits:
    o.write("%s (行%d)\n  前: %s\n  後: %s\n" % (k, i + 1, before, after))
o.close()

# 書いたあと json.loads で狙った値になっているか数える（grepだけで済ませない）
s2 = io.open(PATH, encoding="utf-8", newline="").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", s2, re.S).group(1))
e = [x for x in EV if x["id"] == TARGET][0]
b = open(PATH, "rb").read()
crlf = b.count(b"\r\n")
print("date=%s dateLabel_ok=%s EVENTS=%d CRLF=%d bareLF=%d CRCRLF=%d loneCR=%d"
      % (e["date"], e["dateLabel"] == NEW_LABEL, len(EV), crlf,
         b.count(b"\n") - crlf, b.count(b"\r\r\n"), b.count(b"\r") - crlf))
