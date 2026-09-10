# -*- coding: utf-8 -*-
"""reconcile_rakuten が「未照合」に数えている楽天の枠を、実物で並べて見る。

未照合＝締切が「公演日で締めた(saleEndUnknown)」「売り切れ次第終了(saleUntilSoldOut)」で
突き合わせる相手が無い枠。**正しいと確認できていない枠**なので中身を見てから決める。
"""
import json
import re
import sys
import urllib.parse

sys.stdout.reconfigure(encoding='utf-8')


def raw_url(u):
    m = re.search(r'murl=([^&]+)', u or '')
    return urllib.parse.unquote(m.group(1)) if m else (u or '')


h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
events = json.loads(m.group(2))

n = 0
for e in events:
    rows = []
    for t in e.get('tickets') or []:
        if 'rakuten' not in raw_url(t.get('url')):
            continue
        if t.get('saleEndUnknown') or t.get('saleUntilSoldOut'):
            rows.append(t)
    if not rows:
        continue
    print('== id=%-5s %s' % (e['id'], e['name'][:44]))
    print('   %s' % raw_url((e.get('links') or {}).get('rakuten')))
    for t in rows:
        n += 1
        flag = []
        if t.get('saleEndUnknown'):
            flag.append('saleEndUnknown')
        if t.get('saleUntilSoldOut'):
            flag.append('saleUntilSoldOut')
        if t.get('soldout'):
            flag.append('soldout')
        print('   %-58s date=%s startDate=%s  [%s]'
              % (t['type'][:58], t['date'], t.get('startDate') or '-', '/'.join(flag)))
print('\n未照合の楽天枠 %d枠' % n)
