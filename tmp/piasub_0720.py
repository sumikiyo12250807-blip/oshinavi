# -*- coding: utf-8 -*-
"""新着の _piaSub を見て「ぴあカテゴリ由来（触らない）」と
「_piaSub空/その他＝人が判断する分」を仕分ける。
memory: project_vendor_genre_autoassign（振り分けは_genreをそのまま適用・自分で再分類しない）"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
from check_expired import extract_events_array

events = [e for e in extract_events_array('index.html') if e.get('genre') == 'new']

auto, manual = [], []
for e in events:
    sub = e.get('_piaSub')
    if not sub or 'その他' in sub:
        manual.append(e)
    else:
        auto.append(e)

print(f'=== ぴあカテゴリ由来＝そのまま適用 {len(auto)}件 ===')
for e in auto:
    print(f'  id={e["id"]} _genre={e.get("_genre")} _piaSub={e.get("_piaSub")!r} extra={e.get("_extraGenres")}')
    print(f'      {e.get("name")}')

print(f'\n=== 🚨人が判断する分（_piaSub空 or その他）{len(manual)}件 ===')
for e in manual:
    print(f'  id={e["id"]} _genre={e.get("_genre")} _piaSub={e.get("_piaSub")!r}')
    print(f'      {e.get("name")}')
    print(f'      会場: {e.get("venue")}')
