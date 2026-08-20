# -*- coding: utf-8 -*-
"""劇団☆新感線『アケチコ！』の当日引換券の締切を、ぴあの延長に合わせて更新する。

push直前の reconcile で検出＝ぴあが 〜8/7 8:30 → **〜8/8 8:30** に延ばしていた
（[[feedback_deadline_extended_after_register]]の実例。投入は今朝、延長は日中）。
"""
import json, re, io, sys, shutil, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P = "index.html"
BAK = "index.html.bak_0806_shinkansen"
h = open(P, encoding="utf-8", newline="").read()
NL = "\r\n" if "\r\n" in h else "\n"
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))
if not os.path.exists(BAK):
    shutil.copyfile(P, BAK)

OLD = "当日引換券（福岡 7/24〜8/8公演）〜8/7 8:30"
NEW = "当日引換券（福岡 7/24〜8/8公演）〜8/8 8:30"
n = 0
for e in EVENTS:
    for t in e.get("tickets") or []:
        if t.get("type") == OLD:
            t["type"] = NEW
            t["date"] = "2026-08-08"
            n += 1
assert n == 1, "更新したのは%d枠（1のはず）" % n

new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace("\n", NL)
open(P, "w", encoding="utf-8", newline="").write(
    h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print("劇団☆新感線『アケチコ！』の当日引換券を 〜8/8 8:30 に更新した")
