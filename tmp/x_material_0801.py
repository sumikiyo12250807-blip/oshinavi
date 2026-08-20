# -*- coding: utf-8 -*-
"""X投稿5本ぶんの実データを index.html から丸ごと出す（Fableに渡す素材）"""
import io
import json
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

IDS = [3150, 3174, 2544, 2776, 3481]
raw = open(r"C:\Users\user\oshinavi\index.html", "rb").read().decode("utf-8")
m = re.search(r"const EVENTS = (\[.*?\]);", raw, re.S)
evs = {e["id"]: e for e in json.loads(m.group(1))}

for i in IDS:
    e = evs.get(i)
    if not e:
        print("id=%s 見つからない" % i)
        continue
    print("=" * 60)
    print(json.dumps(e, ensure_ascii=False, indent=2))
