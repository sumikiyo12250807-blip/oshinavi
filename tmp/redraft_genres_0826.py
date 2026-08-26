# -*- coding: utf-8 -*-
"""新着プールの下書きジャンル(_genre)を、直したマッピング表で付け直す。

2026-08-26 の変更（ユーザー決定「ぴあの言う通りにする」）:
  音楽その他 → musicetc（旧 jpop）
  イベントその他 → musicetc（旧 engeki）
  映画その他 → musicetc（旧 engeki）
  スポーツその他 → sports（旧 表に無く名前fallback）
  フェスティバル → fes（旧 意図的に未収載＝人が判断）

⚠️kpop の読み替えだけは残す（ユーザー「①残して」）＝ぴあにK-POP区分が無いだけで、
  ファンはK-POPタブで探すため（feedback_kpop_vs_yougaku）。
"""
import json
import re
import sys

sys.path.insert(0, "tools")
sys.stdout.reconfigure(encoding="utf-8")

import build_pia_entries as bpe

APPLY = "--apply" in sys.argv
h = open("index.html", encoding="utf-8").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))

changed = []
for e in EVENTS:
    if e.get("genre") != "new":
        continue
    sub = e.get("_piaSub") or ""
    if "/" not in sub:
        continue
    cat, s = sub.split("/", 1)
    got = bpe.genre_from_subcat(cat, s, e.get("artist") or "")
    if not got:
        continue
    new_g = got[0]
    old_g = e.get("_genre")
    if new_g != old_g:
        changed.append((e["id"], e.get("artist"), old_g, new_g, sub))
        e["_genre"] = new_g
        if got[1]:
            e["_extraGenres"] = list(got[1])

print("=== 下書きが変わる %d件 ===" % len(changed))
for eid, artist, old, new, sub in changed:
    print("  id=%-5d %-34s %-9s → %-9s （%s）" % (eid, (artist or "")[:34], old, new, sub))

if APPLY and changed:
    open("index.html.bak_0826_redraft", "w", encoding="utf-8").write(h)
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open("index.html", "w", encoding="utf-8").write(
        h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
    print("")
    print("書き込み完了 (backup: index.html.bak_0826_redraft)")
elif not APPLY:
    print("")
    print("（--apply で書き込む）")
