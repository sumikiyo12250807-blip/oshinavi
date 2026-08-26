# -*- coding: utf-8 -*-
"""残りの下書きを「ぴあの言う通り」に揃える（2026-08-26 ユーザー決定）。

  5139 wave to earth … ぴあ「海外ROCK・POPS」だが**韓国のバンド** → kpop
       ⚠️これだけは例外を残す（ユーザー「①残して」／feedback_kpop_vs_yougaku）。
       ぴあにK-POP区分が無いだけで、ファンはK-POPタブで探すため。
  5204 角銅真実 … ぴあ「ジャズ・フュージョン」→ jazz（エージェントはjpop推しだったが、ぴあ優先）
  5222 声優朗読劇フォアレーゼン … ぴあ「朗読・リーディング」→ engeki（同上・seiyuuにしない）
  5278 奈良県民クリスマス … ぴあ「ジャズ・フュージョン」→ jazz（エージェントは判定不能だったが、ぴあ優先）
  5280 サンパレス六甲ディナーショー … ぴあ「演歌・邦楽」→ enka（dinnershowにしない）
  5293 みんなのカンレキオールスターズ … ぴあ「J-POP・ROCK」→ jpop（jazzにしない）
  5300 QUEENS OF THE STONE AGE … ぴあ「J-POP・ROCK」→ jpop（yougakuにしない）
  5240 MORINOMIYA CINEMA CLASSICS … ぴあ「邦画」→ engeki（表の通り。上映イベント）
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

FIX = {5139: "kpop", 5204: "jazz", 5222: "engeki", 5278: "jazz",
       5280: "enka", 5293: "jpop", 5300: "jpop", 5240: "engeki"}
APPLY = "--apply" in sys.argv

h = open("index.html", encoding="utf-8").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))

for e in EVENTS:
    g = FIX.get(e["id"])
    if not g or e.get("genre") != "new":
        continue
    if e.get("_genre") != g:
        print("id=%-5d %-34s %-9s → %-9s （%s）" % (
            e["id"], (e.get("artist") or "")[:34], e.get("_genre"), g, e.get("_piaSub")))
        e["_genre"] = g
    else:
        print("id=%-5d %-34s %s （変更なし）" % (e["id"], (e.get("artist") or "")[:34], g))

if APPLY:
    open("index.html.bak_0826_lastfix", "w", encoding="utf-8").write(h)
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open("index.html", "w", encoding="utf-8").write(
        h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
    print("")
    print("書き込み完了 (backup: index.html.bak_0826_lastfix)")
