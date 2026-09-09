# -*- coding: utf-8 -*-
"""新型（data-event-json）のページに購入ボタンのウィジェットがあるか見る。"""
import json
import re
import sys
import urllib.parse

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_perf_status as P

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
IDS = {7583, 7505, 1, 7582}


def raw_url(u):
    mm = re.search(r'murl=([^&]+)', u or '')
    return urllib.parse.unquote(mm.group(1)) if mm else (u or '')


for e in json.loads(m.group(2)):
    if e['id'] not in IDS:
        continue
    u = raw_url((e.get('links') or {}).get('rakuten'))
    print('===== id=%s %s\n  %s' % (e['id'], e['name'][:40], u))
    try:
        body = P.fetch(u)
    except Exception as ex:
        print('  取得失敗 %r' % (ex,))
        continue
    print('  len=%d' % len(body))
    for kw in ['data-perf', 'performance_btn', 'let ecd', '"eid"', 'data-event-json',
               'salesDisplayStatus', 'cart-button', '予定枚数']:
        print('    %-18s %d' % (kw, body.count(kw)))
    mm = re.search(r'data-event-json=[\'"]([^\'"]+)[\'"]', body)
    if mm:
        print('    event-json: %s' % mm.group(1)[:120])
