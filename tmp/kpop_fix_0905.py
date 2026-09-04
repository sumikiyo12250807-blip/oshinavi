# -*- coding: utf-8 -*-
"""id6538 IRENE & SEULGI は Red Velvet（韓国）のユニット＝ぴあ「音楽/海外ROCK・POPS」を kpop に読み替える。
裏取り: https://redvelvet-jp.net/en/live/tour.php?id=1003061 （IRENE & SEULGI JAPAN TOUR 2026）
memory: feedback_kpop_vs_yougaku（読み替えるのは「海外ROCK・POPS」のときだけ）

🚨 index.html は CRLF。newline="" で読み書きすると json.dumps の \n がそのまま残って
   CRLF が壊れる（2026-09-05に一度やった）。**読みも書きも newline 未指定**にして
   Python のテキストモードに往復させる＝heal_stale_deadlines.py と同じ書き方。"""
import json, re, io, datetime, sys

PATH = "index.html"
SRC = sys.argv[1] if len(sys.argv) > 1 else PATH
TARGET = 6538

h = open(SRC, encoding="utf-8").read()
m = re.search(r"(const EVENTS = )(\[.*?\])(;\n)", h, re.S)
events = json.loads(m.group(2))
by = {e["id"]: e for e in events}
e = by[TARGET]
assert e.get("_piaSub") == "音楽/海外ROCK・POPS", e.get("_piaSub")
assert e.get("genre") == "new", e.get("genre")
before = e.get("_genre")
e["_genre"] = "kpop"

bak = "index.html.bak_%s_kpop" % datetime.date.today().strftime("%m%d")
new_arr = json.dumps(events, ensure_ascii=False, indent=2)
open(PATH, "w", encoding="utf-8").write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print("id=%d _genre %s -> kpop (src=%s)" % (TARGET, before, SRC))
