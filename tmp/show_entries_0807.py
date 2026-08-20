# -*- coding: utf-8 -*-
"""指定idのエントリを index.html から抜いて表示（8/7 朝の変換用）。"""
import io
import json
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

IDS = [187, 513, 1026, 2243, 3475, 3513]
b = open(r"C:\Users\user\oshinavi\index.html", "rb").read().decode("utf-8").replace("\r\n", "\n")

for eid in IDS:
    m = re.search(r'\n  \{\n    "id": %d,\n.*?\n  \}(?=,\n  \{\n    "id"|\n\])' % eid, b, re.S)
    if not m:
        print("id=%d 見つからない" % eid)
        continue
    print("=" * 70)
    print(m.group(0).strip())
