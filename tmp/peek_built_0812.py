# -*- coding: utf-8 -*-
"""構築済みJSONから指定idのエントリを取り出して見る。"""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

path = sys.argv[1]
ids = [int(x) for x in sys.argv[2].split(",")]
for e in json.load(open(path, encoding="utf-8-sig")):
    if e["id"] in ids:
        print(json.dumps(e, ensure_ascii=False, indent=2))
