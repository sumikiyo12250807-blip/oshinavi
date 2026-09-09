# -*- coding: utf-8 -*-
"""売り状態を調べられなかった9件が、どの形で買える/売り切れを書いているかを見る。"""
import json
import re
import sys
import urllib.parse

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_perf_status as P

IDS = {1, 3674, 7505, 7506, 7507, 7582, 7583, 7584, 7585}


def raw_url(u):
    m = re.search(r'murl=([^&]+)', u or '')
    return urllib.parse.unquote(m.group(1)) if m else (u or '')


h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
WORDS = ['予定枚数終了', '完売', '売切', 'SOLD', '販売終了', '受付終了',
         'cart-button', 'data-perf', 'data-event-json', 'salesDisplayStatus',
         'cart/performances/agreement']

for e in json.loads(m.group(2)):
    if e['id'] not in IDS:
        continue
    u = raw_url((e.get('links') or {}).get('rakuten'))
    print('== id=%-5s %s' % (e['id'], e['name'][:40]))
    print('   %s' % u)
    try:
        body = P.fetch(u)
    except Exception as ex:
        print('   取得失敗 %r\n' % (ex,))
        continue
    hits = {w: body.count(w) for w in WORDS if body.count(w)}
    print('   %s' % hits)
    # 「予定枚数終了」がどの文脈に出るか（席種の値段表か、ボタンか）
    for mm in list(re.finditer('予定枚数終了', body))[:2]:
        i = mm.start()
        print('     …%s' % re.sub(r'\s+', ' ', P.strip_tags(body[max(0, i - 160):i + 60])))
    print()
