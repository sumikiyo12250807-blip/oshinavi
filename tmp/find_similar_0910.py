# -*- coding: utf-8 -*-
"""統合の相手が見つからなかった名前について、似ている既存エントリを探す。

🚨部分一致で畳むのは禁止（「新日本フィル」が消える）ので、**候補を出すだけ**。
決めるのは1件ずつ中身を見てから。
"""
import io
import json
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')
NAMES = ['イルカ', '佐藤竹善', '吉幾三', 'キーウ・クラシック・バレエ', 'ＯＺアカデミー女子プロレス']


def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　]+', '', s).lower()


h = io.open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
events = json.loads(m.group(2))

for n in NAMES:
    k = norm(n)
    print('== %s' % n)
    for e in events:
        nm = norm(e.get('name'))
        ar = norm(e.get('artist'))
        if k in nm or k in ar or nm in k:
            ls = e.get('links') or {}
            print('   id=%-5s [%s] %-40s %s  %s'
                  % (e['id'], e.get('genre'), (e.get('name') or '')[:40], e.get('date'),
                     ls.get('pia') or ''))
    print()
