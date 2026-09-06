# -*- coding: utf-8 -*-
"""6925 HUE with「心の瞳合唱団」を kpop に振り分ける（2026-09-06 ユーザー決定「HUEはKPOP」）。

ぴあ区分は「音楽/海外ROCK・POPS」。HUEは韓国・釜山のポペラ（ポップス+オペラ）デュオなので、
feedback_kpop_vs_yougaku の例外条項（海外ROCK・POPS × 韓国 → kpop）をそのまま当てる。
中身がクラシック寄りでも読み替える、というのが今回の確認事項。
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

APPLY = "--apply" in sys.argv
TARGET = 6925
GENRE = "kpop"
DRAFT = ("_genre", "_extraGenres", "_piaSub", "_srcgenre")

h = open("index.html", encoding="utf-8").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))

hit = None
for e in EVENTS:
    if e["id"] != TARGET:
        continue
    hit = e
    print("id=%d %s" % (e["id"], e.get("artist")))
    print("  ぴあ区分 _piaSub = %s" % e.get("_piaSub"))
    print("  下書き   _genre  = %s" % e.get("_genre"))
    print("  genre    %s → %s" % (e.get("genre"), GENRE))
    e["genre"] = GENRE
    for k in DRAFT:
        e.pop(k, None)

if not hit:
    print("見つからない id=%d" % TARGET)
    sys.exit(1)

mo = re.search(r"(  const NEW_ORDER = \[)([^\]]*)(\];)", h)
ids = [int(x) for x in mo.group(2).replace("\n", "").split(",") if x.strip()]
left = [i for i in ids if i != TARGET]
print("NEW_ORDER %d件 → %d件" % (len(ids), len(left)))

if APPLY:
    open("index.html.bak_0906_hue", "w", encoding="utf-8").write(h)
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    out = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]
    mo2 = re.search(r"(  const NEW_ORDER = \[)([^\]]*)(\];)", out)
    out = out[:mo2.start()] + mo2.group(1) + ", ".join(str(i) for i in left) + mo2.group(3) + out[mo2.end():]
    open("index.html", "w", encoding="utf-8").write(out)
    with open("logs/assigned_2026-09-06.md", "a", encoding="utf-8") as f:
        f.write("\n\n## 追加の振り分け（夜・ユーザー決定）\n\n")
        f.write("| id | 公演名 | ジャンル | 確認用URL |\n|---|---|---|---|\n")
        f.write("| 6925 | HUE with「心の瞳合唱団」 | kpop | %s |\n"
                % ((hit.get("links") or {}).get("pia") or "-"))
        f.write("\nぴあ区分は「音楽/海外ROCK・POPS」。HUEは韓国・釜山のポペラ（ポップス+オペラ）デュオ。\n")
        f.write("ユーザー決定「HUEはKPOP」＝**中身がクラシック寄りでも、韓国なら kpop に読み替える**。\n")
    print("書き込み完了 (backup: index.html.bak_0906_hue / logs/assigned_2026-09-06.md に追記)")
else:
    print("（--apply で書き込む）")
