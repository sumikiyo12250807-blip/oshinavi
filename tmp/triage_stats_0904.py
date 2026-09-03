# -*- coding: utf-8 -*-
"""9/3のtriage結果の内訳を数える（なぜ新規投入が少なかったかの分解）。"""
import json, io, os

for path in ["tmp/_triage_0903.json", "tmp/_merge_pending_0903.json"]:
    if not os.path.exists(path):
        print("MISSING %s" % path)
        continue
    d = json.load(io.open(path, encoding="utf-8"))
    print("== %s ==" % path)
    if isinstance(d, dict):
        for k, v in d.items():
            n = len(v) if isinstance(v, (list, dict)) else 1
            print("   %-20s %s" % (k, n))
    elif isinstance(d, list):
        print("   list len=%d" % len(d))
