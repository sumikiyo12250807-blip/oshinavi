# -*- coding: utf-8 -*-
"""救済対象エントリを index.html から抜いて表示（8/7）。"""
import io
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

IDS = [144, 185, 717, 813, 3065]
b = open(r"C:\Users\user\oshinavi\index.html", "rb").read().decode("utf-8").replace("\r\n", "\n")

for eid in IDS:
    m = re.search(r'\n  \{\n    "id": %d,\n.*?\n  \}(?=,\n  \{\n    "id"|\n\])' % eid, b, re.S)
    print("=" * 70)
    print(m.group(0).strip() if m else "id=%d 見つからない" % eid)
