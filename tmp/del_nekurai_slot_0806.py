# -*- coding: utf-8 -*-
"""ネクライトーキーの大阪11/3（心斎橋SUNHALL）ローチケ枠を消す（ユーザーOK 2026-08-06）。

ローチケの実画面で確認済み＝「**予定枚数終了**」／受付期間 8/5 21:00〜10/25 22:00。
ぴあにはこの公演の枠が無く、完売した枠だけが残っていた（画面からも消えていた）。
OSHINAVIは買えるもののカウントダウン（[[feedback_oshinavi_concept]]）なので枠を落とす。
会場一覧からも心斎橋SUNHALLを外す。
"""
import json, re, io, sys, shutil, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P = "index.html"
BAK = "index.html.bak_0806_nekurai_del"
h = open(P, encoding="utf-8", newline="").read()
NL = "\r\n" if "\r\n" in h else "\n"
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))
if not os.path.exists(BAK):
    shutil.copyfile(P, BAK)

hit = 0
for e in EVENTS:
    if (e.get("artist") or "") != "ネクライトーキー":
        continue
    hit += 1
    before = len(e["tickets"])
    e["tickets"] = [t for t in e["tickets"] if "l-tike.com" not in (t.get("url") or "")]
    print("枠 %d → %d" % (before, len(e["tickets"])))
    v = e.get("venue") or ""
    e["venue"] = v.replace("／心斎橋SUNHALL", "").replace("心斎橋SUNHALL／", "")
    print("会場: %s" % e["venue"])
assert hit == 1, "ネクライトーキーが%d件" % hit

new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace("\n", NL)
open(P, "w", encoding="utf-8", newline="").write(
    h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print("ネクライトーキーの大阪11/3（完売）を削除した")
