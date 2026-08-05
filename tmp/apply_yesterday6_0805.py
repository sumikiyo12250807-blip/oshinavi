# -*- coding: utf-8 -*-
"""昨日(8/4)の相談6件のジャンル案を下書きに反映する。ユーザー「そのままでいいわ」＝案どおりでOK（2026-08-05）。

  3694 駒田早代 津軽三味線ライブ   fes    → dento （和楽器＝邦楽。演歌ではない）
  3699 NOISEMAKER              rock   → jpop  （ぴあがJ-POP・ROCKで一括＝人が細分しない）
  3672 ロボットアニメ上映会         engeki → anime
  3676 福岡謎解き街歩き           engeki → kids + extraGenres:[engeki]
  3673 金沢おいも万博             kids   → fes
  3685 秋酒祭 愛知               kids   → fes  （酒イベントなのでkidsは誤り）

🚨 genre は "new" のまま＝プールの件数を1件も動かさない（[[feedback_new_pool_ok_before_assign]]）。
"""
import io
import json
import os
import re
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = r"C:\Users\user\oshinavi"
IDX = os.path.join(ROOT, "index.html")
BAK = os.path.join(ROOT, "index.html.bak_0805_yesterday6")

PLAN = {
    3694: ("dento", []),
    3699: ("jpop", []),
    3672: ("anime", []),
    3676: ("kids", ["engeki"]),
    3673: ("fes", []),
    3685: ("fes", []),
}

h = io.open(IDX, encoding="utf-8", newline="").read()
NL = "\r\n" if "\r\n" in h else "\n"
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))

n = 0
for e in EVENTS:
    if e["id"] in PLAN:
        g, ex = PLAN[e["id"]]
        print("id%-5d %-8s%-12s → %-8s%-12s %s" % (
            e["id"], e.get("_genre"),
            "+" + ",".join(e.get("_extraGenres") or []) if e.get("_extraGenres") else "",
            g, "+" + ",".join(ex) if ex else "", (e.get("artist") or "")[:36]))
        e["_genre"] = g
        e["_extraGenres"] = ex
        assert e["genre"] == "new", "genreがnewでない: id%d" % e["id"]
        n += 1

assert n == len(PLAN), "対象が足りない: %d/%d" % (n, len(PLAN))
shutil.copyfile(IDX, BAK)
arr = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace("\n", NL)
io.open(IDX, "w", encoding="utf-8", newline="").write(h[:m.start()] + m.group(1) + arr + m.group(3) + h[m.end():])
print("\n✅ %d件の下書きを更新（genreは全件 new のまま）" % n)
