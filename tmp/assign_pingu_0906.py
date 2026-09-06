# -*- coding: utf-8 -*-
"""6613 可愛いだけじゃない!?ピングー展 を振り分ける（保留の解除）。

なぜ2日も新着に居座っていたか＝9/5に「ぴあが eventCd を無効化した」と判断して保留にしたが、
2026-09-06 に実ページを開いたら**普通に生きていた**（会期・券種・「販売期間中」まで表示される）。
9/5は混雑ページか何かを掴んで「死んだ」と読み違えたとしか考えられない。
公式（pingu-exhibit26.jp）でも前売9/5発売・売り場4つを確認。reconcile も 1/1 一致。

🚨教訓＝「ぴあのページが死んだ」と判断したら、**保留にした翌日に必ず開き直す**。
保留は寝かせる場所ではない（feedback_pia_eventcd_gone / logs/hold_2026-09-05.md）。
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

APPLY = "--apply" in sys.argv
TARGET = 6613
DRAFT = ("_genre", "_extraGenres", "_piaSub", "_srcgenre")

h = open("index.html", encoding="utf-8").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))

hit = None
for e in EVENTS:
    if e["id"] != TARGET:
        continue
    hit = e
    g = e.get("_genre")
    print("id=%d %s" % (e["id"], e.get("artist")))
    print("  ぴあ区分 _piaSub = %s" % e.get("_piaSub"))
    print("  genre    %s → %s（ぴあの言う通り）" % (e.get("genre"), g))
    e["genre"] = g
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
    open("index.html.bak_0906_pingu", "w", encoding="utf-8").write(h)
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    out = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]
    mo2 = re.search(r"(  const NEW_ORDER = \[)([^\]]*)(\];)", out)
    out = out[:mo2.start()] + mo2.group(1) + ", ".join(str(i) for i in left) + mo2.group(3) + out[mo2.end():]
    open("index.html", "w", encoding="utf-8").write(out)
    with open("logs/assigned_2026-09-06.md", "a", encoding="utf-8") as f:
        f.write("\n| 6613 | 可愛いだけじゃない!?ピングー展 | art | %s |\n"
                % ((hit.get("links") or {}).get("pia") or "-"))
        f.write("\n🚨9/5に「ぴあがeventCdを無効化した」として保留していたが、9/6に実ページを開いたら\n")
        f.write("**生きていた**（会期・券種・販売期間中まで表示）。9/5の読み違い。reconcile 1/1 一致。\n")
        f.write("公式 https://pingu-exhibit26.jp/ticket/ でも前売9/5発売を確認。\n")
    print("書き込み完了 (backup: index.html.bak_0906_pingu)")
else:
    print("（--apply で書き込む）")
