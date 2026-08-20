# -*- coding: utf-8 -*-
"""kaidan_grow_built.json から id3804（配信版）だけ取り出す。id44 は既存エントリの育成で適用済み。"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = r"C:\Users\user\oshinavi"
d = json.load(io.open(os.path.join(ROOT, "tmp", "kaidan_grow_built.json"), encoding="utf-8-sig"))
only = [e for e in d if e["id"] == 3804]
json.dump(only, io.open(os.path.join(ROOT, "tmp", "kaidan_3804.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("→ tmp/kaidan_3804.json （%d件）" % len(only))
