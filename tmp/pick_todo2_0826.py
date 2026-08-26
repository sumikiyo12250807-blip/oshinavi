# -*- coding: utf-8 -*-
"""merge_todo_0826.json から指定idだけ抜いたテスト用のplanを作る。
使い方: python tmp/pick_todo_0826.py 492,4489,1333 tmp/merge_test_0826.json"""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

ids = set(sys.argv[1].split(","))
out = sys.argv[2]
todo = json.load(open("tmp/merge_todo2_0826.json", encoding="utf-8"))
pick = {k: v for k, v in todo.items() if k in ids}
json.dump(pick, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("%d件 → %s" % (len(pick), out))
for k, v in pick.items():
    print("  id=%s ＋%d URL" % (k, len(v)))
