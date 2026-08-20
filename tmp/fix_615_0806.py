# -*- coding: utf-8 -*-
"""615 稲垣潤一に、昼のヒールで落ちた「埼玉 9/5公演の一般発売」を戻す。

ぴあ実ページ(eventCd=2619393)を単発で叩いて確認済み＝
  [受付中] 2026-09-05 埼玉県 久喜総合文化会館 大ホール 一般発売 〜2026/9/1(火) 23:59
"""
import json, re, io, sys, shutil, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P = "index.html"
BAK = "index.html.bak_0806_fix615"
h = open(P, encoding="utf-8", newline="").read()
NL = "\r\n" if "\r\n" in h else "\n"
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))
if not os.path.exists(BAK):
    shutil.copyfile(P, BAK)

NEW = {"type": "一般発売（埼玉 9/5公演）〜9/1 23:59", "date": "2026-09-01",
       "url": "https://t.pia.jp/pia/event/event.do?eventCd=2619393"}

hit = 0
for e in EVENTS:
    if e["id"] != 615:
        continue
    hit += 1
    assert not any(t["type"] == NEW["type"] for t in e["tickets"]), "すでにある"
    e["tickets"].insert(0, NEW)
assert hit == 1

new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace("\n", NL)
open(P, "w", encoding="utf-8", newline="").write(
    h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print("615 に「一般発売（埼玉 9/5公演）〜9/1 23:59」を戻した")
