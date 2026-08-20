# -*- coding: utf-8 -*-
"""id4020 日食なつこ の各枠のURLを機械抽出（プレリザーブ枠の出所確認）"""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools'))
from check_expired import extract_events_array
sys.stdout.reconfigure(encoding='utf-8')

for e in extract_events_array('index.html'):
    if e.get('id') in (4020, 3153, 3316):
        print('=== id=%d %s' % (e['id'], e.get('name')))
        print(json.dumps(e, ensure_ascii=False, indent=1))
