# -*- coding: utf-8 -*-
"""投入対象の下書きジャンルと、その根拠(_piaSub)を並べて見る。"""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

for e in json.load(open("tmp/all_new_0812.json", encoding="utf-8-sig")):
    print("%d\t%s\t_piaSub=%s\t%s\t%s" % (
        e["id"], e["_genre"], e.get("_piaSub") or "(空)", e["name"][:34], e.get("venue", "")[:20]))
