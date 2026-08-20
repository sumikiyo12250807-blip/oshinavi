# -*- coding: utf-8 -*-
"""3807 オカルト超会議の同日2公演を、バッジの（…公演）内に開演時刻を入れる形へ直す。

[[feedback_same_day_show_time_badge]]＝同一会場・同日で時間だけ違う公演は
「（神奈川 8/21 15:00公演）」の形にする。【1部 15:00】のように券種側に持たせると、
画面では公演descriptorが同じに見えて見分けられない（reconcile_eplusのh-時刻欠が検知）。
"""
import json, re, io, sys, shutil, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P = "index.html"
BAK = "index.html.bak_0806_3807_time"
h = open(P, encoding="utf-8", newline="").read()
NL = "\r\n" if "\r\n" in h else "\n"
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))
if not os.path.exists(BAK):
    shutil.copyfile(P, BAK)

REP = {
    "一般発売【1部 15:00】（神奈川 8/21公演）〜8/19 18:00":
        "一般発売【1部】（神奈川 8/21 15:00公演）〜8/19 18:00",
    "一般発売【2部 18:30】（神奈川 8/21公演）〜8/19 18:00":
        "一般発売【2部】（神奈川 8/21 18:30公演）〜8/19 18:00",
    "一般発売【1部 15:00】（神奈川 8/22公演）〜8/20 18:00":
        "一般発売【1部】（神奈川 8/22 15:00公演）〜8/20 18:00",
    "一般発売【2部 18:30】（神奈川 8/22公演）〜8/20 18:00":
        "一般発売【2部】（神奈川 8/22 18:30公演）〜8/20 18:00",
}

n = 0
for e in EVENTS:
    if e["id"] != 3807:
        continue
    for t in e.get("tickets") or []:
        if t["type"] in REP:
            t["type"] = REP[t["type"]]
            n += 1
assert n == 4, "置換できたのは%d枠（4のはず）" % n

new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace("\n", NL)
open(P, "w", encoding="utf-8", newline="").write(
    h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print("3807 のバッジ4枠に開演時刻を入れた")
