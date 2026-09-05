# -*- coding: utf-8 -*-
"""新着プール（genre:"new"）のぴあ由来を、下書き _genre で確定する。
2026-09-06 朝の振り分け。ジャンルは「ぴあの言う通り」（feedback_genre_pia_asis_and_other）。
別エージェントの独立再導出で 71/71 照合済み（_piaSub → PIA_GENRE_MAP でゼロから導出）。

SKIP（プールに残す）:
  6613 ピングー展   … ぴあが eventCd を無効化・他社未確認（logs/hold_2026-09-05.md）
  6911 SHIN SOOHYUN … 公演2026-09-05 で終了済み＝削除対象
  6925 HUE          … 韓国のポペラ・デュオ。ぴあ区分は「海外ROCK・POPS」だが
                      kpop へ読み替えるかユーザーに確認中
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

SKIP = {6613, 6911, 6925}
DRAFT = ("_genre", "_extraGenres", "_piaSub", "_srcgenre")
APPLY = "--apply" in sys.argv

h = open("index.html", encoding="utf-8").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))


def is_pia(e):
    blob = json.dumps(e, ensure_ascii=False)
    return "t.pia.jp" in blob or "ticket.pia.jp" in blob


done = []
skipped = []
for e in EVENTS:
    if e.get("genre") != "new":
        continue
    if not is_pia(e):
        continue                      # e+ 等は振り分けない（ユーザーが新着タブで確認）
    if e["id"] in SKIP:
        skipped.append(e["id"])
        continue
    g = e.get("_genre")
    if not g:
        print("⚠️ 下書きジャンル無し id=%d %s" % (e["id"], e.get("artist")))
        continue
    extra = e.get("_extraGenres") or []
    done.append((e["id"], e.get("artist") or e.get("title") or "", g, extra,
                 (e.get("links") or {}).get("pia") or ""))
    e["genre"] = g
    if extra:
        e["extraGenres"] = extra
    for k in DRAFT:
        e.pop(k, None)

for i, a, g, x, u in done:
    print("id=%-5d %-40s new → %s%s" % (i, a[:40], g, ("（+%s）" % ",".join(x)) if x else ""))
print("")
print("振り分け %d件 / プールに残す(ぴあ) %d件 %s" % (len(done), len(skipped), sorted(skipped)))

mo = re.search(r"(  const NEW_ORDER = \[)([^\]]*)(\];)", h)
ids = [int(x) for x in mo.group(2).replace("\n", "").split(",") if x.strip()]
assigned = {d[0] for d in done}
left = [i for i in ids if i not in assigned]
print("NEW_ORDER %d件 → %d件" % (len(ids), len(left)))

if APPLY:
    open("index.html.bak_0906_assign", "w", encoding="utf-8").write(h)
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    out = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]
    mo2 = re.search(r"(  const NEW_ORDER = \[)([^\]]*)(\];)", out)
    out = out[:mo2.start()] + mo2.group(1) + ", ".join(str(i) for i in left) + mo2.group(3) + out[mo2.end():]
    open("index.html", "w", encoding="utf-8").write(out)
    with open("logs/assigned_2026-09-06.md", "w", encoding="utf-8") as f:
        f.write("# 振り分け 2026-09-06（朝の便）\n\n")
        f.write("ぴあ由来の新着を `_piaSub` → `PIA_GENRE_MAP` の機械写しで確定した。\n")
        f.write("別エージェントが `_piaSub` からゼロで再導出して **71/71 照合**、食い違いは 6911・6925 の2件のみ。\n\n")
        f.write("| id | 公演名 | ジャンル | 確認用URL |\n|---|---|---|---|\n")
        for i, a, g, x, u in done:
            gg = g + ("+" + ",".join(x) if x else "")
            f.write("| %d | %s | %s | %s |\n" % (i, a.replace("|", "／"), gg, u))
        f.write("\n## プールに残したもの\n\n")
        f.write("- 6613 可愛いだけじゃない!?ピングー展 … ぴあが eventCd を無効化・他社未確認\n")
        f.write("- 6911 SHIN SOOHYUN … 公演2026-09-05 で終了済み＝削除対象\n")
        f.write("- 6925 HUE with「心の瞳合唱団」 … 韓国のポペラ・デュオ。ぴあ区分は「海外ROCK・POPS」\n")
        f.write("  だが kpop へ読み替えるかユーザーに確認中\n")
    print("書き込み完了 (backup: index.html.bak_0906_assign / logs/assigned_2026-09-06.md)")
else:
    print("（--apply で書き込む）")
