# -*- coding: utf-8 -*-
"""新着プール（genre:"new"）を、ぴあ区分から機械で写した下書き _genre で確定する。
2026-08-29 朝の振り分け。ジャンルは「ぴあの言う通り」（feedback_genre_pia_asis_and_other）。
_extraGenres があれば extraGenres として残す（バレエ=classic+engeki など）。
除外したい id は SKIP に入れる（相談中の件はプールに残す）。
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

ONLY = set(range(5595, 5656))   # 別エージェント2本の再導出が済んだ61件だけ
SKIP = set()          # 保留にする id（相談中）
DRAFT = ("_genre", "_extraGenres", "_piaSub", "_srcgenre")
APPLY = "--apply" in sys.argv

h = open("index.html", encoding="utf-8").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))

done = []
for e in EVENTS:
    if e.get("genre") != "new" or e["id"] in SKIP or e["id"] not in ONLY:
        continue
    g = e.get("_genre")
    if not g:
        print("⚠️ 下書きジャンル無し id=%d %s" % (e["id"], e.get("artist")))
        continue
    extra = e.get("_extraGenres") or []
    done.append((e["id"], e.get("artist") or "", g, extra, (e.get("links") or {}).get("pia") or ""))
    e["genre"] = g
    if extra:
        e["extraGenres"] = extra
    for k in DRAFT:
        e.pop(k, None)

for i, a, g, x, u in done:
    print("id=%-5d %-40s new → %s%s" % (i, a[:40], g, ("（+%s）" % ",".join(x)) if x else ""))
print("")
print("振り分け %d件 / 保留 %d件" % (len(done), len(SKIP)))

mo = re.search(r"(  const NEW_ORDER = \[)([^\]]*)(\];)", h)
ids = [int(x) for x in mo.group(2).replace("\n", "").split(",") if x.strip()]
assigned = {d[0] for d in done}
left = [i for i in ids if i not in assigned]
print("NEW_ORDER %d件 → %d件" % (len(ids), len(left)))

if APPLY:
    open("index.html.bak_0829_assign", "w", encoding="utf-8").write(h)
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    out = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]
    mo2 = re.search(r"(  const NEW_ORDER = \[)([^\]]*)(\];)", out)
    out = out[:mo2.start()] + mo2.group(1) + ", ".join(str(i) for i in left) + mo2.group(3) + out[mo2.end():]
    open("index.html", "w", encoding="utf-8").write(out)
    # 振り分けログ
    with open("logs/assigned_2026-08-29.md", "w", encoding="utf-8") as f:
        f.write("# 振り分け 2026-08-29（朝の便）\n\n")
        f.write("| id | 公演名 | ジャンル | 確認用URL |\n|---|---|---|---|\n")
        for i, a, g, x, u in done:
            gg = g + ("+" + ",".join(x) if x else "")
            f.write("| %d | %s | %s | %s |\n" % (i, a.replace("|", "／"), gg, u))
    print("書き込み完了 (backup: index.html.bak_0829_assign / logs/assigned_2026-08-29.md)")
else:
    print("（--apply で書き込む）")
