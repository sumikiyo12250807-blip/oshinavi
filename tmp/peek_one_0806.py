# -*- coding: utf-8 -*-
"""構築結果から1件を全部出す。"""
import json, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
built = json.load(open(sys.argv[1], encoding="utf-8-sig"))
want = int(sys.argv[2])
for e in built:
    if e["id"] == want:
        print(json.dumps(e, ensure_ascii=False, indent=1))
