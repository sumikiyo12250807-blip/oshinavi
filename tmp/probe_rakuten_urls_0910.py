# -*- coding: utf-8 -*-
"""問題のエントリが何本の楽天URLを持っているかを見る。"""
import json
import re
import sys
import urllib.parse

sys.stdout.reconfigure(encoding='utf-8')

IDS = {1, 3224, 3228, 3239, 3244, 7493}


def raw_url(u):
    m = re.search(r'murl=([^&]+)', u or '')
    return urllib.parse.unquote(m.group(1)) if m else (u or '')


h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
for e in json.loads(m.group(2)):
    if e['id'] not in IDS:
        continue
    print('== id=%s %s' % (e['id'], e['name'][:40]))
    print('   links.rakuten = %s' % raw_url((e.get('links') or {}).get('rakuten')))
    for t in e.get('tickets') or []:
        u = raw_url(t.get('url'))
        if 'rakuten' in u:
            print('   ticket %-46s -> %s' % (t['type'][:46], u))
