# -*- coding: utf-8 -*-
"""ビルド結果JSONの中身を要点だけ表示（読むだけ）。使い方: python tmp/show_built_0911.py <built.json>"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
for e in json.load(open(sys.argv[1], encoding='utf-8-sig')):
    print('id%s %s | date=%s | %s | %s' % (e.get('id'), e.get('name'), e.get('date'), e.get('prefecture'), (e.get('venue') or '')[:40]))
    for t in e.get('tickets') or []:
        print('   - %s | date=%s start=%s url=%s' % (t.get('type'), t.get('date'), t.get('startDate'), (t.get('url') or '')[-30:]))
