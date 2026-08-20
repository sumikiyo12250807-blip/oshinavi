# -*- coding: utf-8 -*-
"""削除候補のエントリ名とぴあURLを index.html から機械抽出する（手打ち禁止）"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
from check_expired import extract_events_array  # 既存ロジックを流用

IDS = [104, 205, 507, 814, 1873, 1885, 1070, 1700, 2068, 2069, 2073, 2273, 2835]

data = extract_events_array("index.html")
by_id = {e.get("id"): e for e in data}

for i in IDS:
    e = by_id.get(i)
    if not e:
        print(f"id={i} 見つからない")
        continue
    links = e.get("links") or {}
    url = links.get("pia") or links.get("rakuten") or links.get("eplus") or links.get("official") or "(URL無し)"
    print(f"{e.get('name')} | {e.get('date')} | {url}")
