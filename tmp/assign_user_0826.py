# -*- coding: utf-8 -*-
"""ユーザーが決めたジャンルを適用する（2026-08-26 夜）。
  5098 第46回マーチングバンド東京都大会 → classic（ユーザー回答「クラシック」）
  5119 第2回 杉良太郎に会いたい         → enka   （ユーザー回答「演歌」）
  5120 PBO主催 カクテル&バーフェスタ2026 → gourmet（ユーザー回答「グルメ」）
下書きフィールドを消して genre を確定し、NEW_ORDER からも外す。
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

DECIDE = {5098: "classic", 5119: "enka", 5120: "gourmet"}
DRAFT = ("_genre", "_extraGenres", "_piaSub", "_srcgenre")
APPLY = "--apply" in sys.argv

h = open("index.html", encoding="utf-8").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))

for e in EVENTS:
    g = DECIDE.get(e["id"])
    if not g or e.get("genre") != "new":
        continue
    extra = e.get("_extraGenres") or []
    print("id=%-5d %-36s new → %s%s" % (
        e["id"], (e.get("artist") or "")[:36], g, ("（+%s）" % ",".join(extra)) if extra else ""))
    e["genre"] = g
    if extra:
        e["extraGenres"] = extra
    for k in DRAFT:
        e.pop(k, None)

# NEW_ORDER から外す
mo = re.search(r"(  const NEW_ORDER = \[)([^\]]*)(\];)", h)
ids = [int(x) for x in mo.group(2).replace("\n", "").split(",") if x.strip()]
left = [i for i in ids if i not in DECIDE]
print("")
print("NEW_ORDER %d件 → %d件" % (len(ids), len(left)))

if APPLY:
    open("index.html.bak_0826_userassign", "w", encoding="utf-8").write(h)
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    out = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]
    mo2 = re.search(r"(  const NEW_ORDER = \[)([^\]]*)(\];)", out)
    out = out[:mo2.start()] + mo2.group(1) + ", ".join(str(i) for i in left) + mo2.group(3) + out[mo2.end():]
    open("index.html", "w", encoding="utf-8").write(out)
    print("書き込み完了 (backup: index.html.bak_0826_userassign)")
else:
    print("（--apply で書き込む）")
