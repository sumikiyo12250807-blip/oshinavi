# -*- coding: utf-8 -*-
"""assign_genres.py に渡す --exclude を作る＝プールのうち「振り分けない全部」。
振り分けるのは、あたしの下書きと別エージェントの独立判定が**一致した72件**だけ。"""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

ok = set(json.load(open("tmp/assign_ok_0826.json", encoding="utf-8")))
src = open("index.html", encoding="utf-8").read()
m = re.search(r"const EVENTS = (\[.*?\]);\n", src, re.S)
pool = [e["id"] for e in json.loads(m.group(1)) if e.get("genre") == "new"]
skip = sorted(set(pool) - ok)

print("プール %d件 / 振り分け %d件 / 残す %d件" % (len(pool), len(ok), len(skip)))
print("")
print("--exclude " + ",".join(str(i) for i in skip))
open("tmp/exclude_0826.txt", "w", encoding="utf-8").write(",".join(str(i) for i in skip))
