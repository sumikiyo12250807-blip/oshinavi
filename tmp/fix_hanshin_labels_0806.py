# -*- coding: utf-8 -*-
"""阪神4試合の券種名を check_badges が通る形（販売種別〔席種〕）に直す。

check_badges は「券種名に全角／」をぴあパース化けの兆候として弾く。
統合で付ける席種ラベルは 〔…〕 に入れる約束（tools/check_badges.py の除外規則）。
  例: 「アルプス楽楽シート／一般発売（兵庫 9/15公演）…」
   →  「一般発売〔アルプス楽楽シート〕（兵庫 9/15公演）…」
index.html は CRLF を保って書き戻す（[[feedback_index_html_crlf_preserve]]）。
"""
import json, re, io, sys, shutil, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P = "index.html"
BAK = "index.html.bak_0806_hanshin_labels"
TARGET = {3841, 3849, 3853, 3858}

h = open(P, encoding="utf-8", newline="").read()
NL = "\r\n" if "\r\n" in h else "\n"
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))

if not os.path.exists(BAK):
    shutil.copyfile(P, BAK)

fixed = 0
for e in EVENTS:
    if e["id"] not in TARGET:
        continue
    for t in e.get("tickets") or []:
        typ = t["type"]
        head, sep, rest = typ.partition("（")
        if "／" not in head:
            continue
        seat, _, sale = head.partition("／")
        seat, sale = seat.strip(), sale.strip()
        t["type"] = "%s〔%s〕%s%s" % (sale, seat, sep, rest)
        fixed += 1

new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace("\n", NL)
open(P, "w", encoding="utf-8", newline="").write(
    h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print("券種名を〔席種〕形に修正: %d枠" % fixed)
