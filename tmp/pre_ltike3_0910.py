# -*- coding: utf-8 -*-
"""ローチケ独占3件を入れる前の下ごしらえ＝重複チェックと新着プールの現況。"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
h = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
no = json.loads(re.search(r'const NEW_ORDER = (\[[^\]]*\])', h, re.S).group(1))

print('EVENTS %d / maxid %d / NEW_ORDER %d' % (len(ev), max(e['id'] for e in ev), len(no)))
print('NEW_ORDER 末尾12:', no[-12:])
print('NEW_ORDER 先頭6 :', no[:6])

# 重複チェック（[[feedback_check_duplicates]]）
KEYS = ['別府葉子', '野田かつひこ', 'REVERSE EDGE', 'ＲＥＶＥＲＳＥ', '環ROY', 'ぷにぷに電機',
        'SUPERNOVA', 'ＳＵＰＥＲＮＯＶＡ', '国際楽器社', '石橋文化']
for k in KEYS:
    hit = [e for e in ev
           if k in (e.get('artist') or '') + (e.get('name') or '') + (e.get('venue') or '')]
    print('  %-14s %d件 %s' % (k, len(hit), [(e['id'], e['name'][:26]) for e in hit[:3]]))

# 今日入れた分（7812以降）
today = [e for e in ev if e['id'] >= 7812]
print('\n7812以降 %d件:' % len(today))
for e in today:
    print('  id%-5d %-8s %s' % (e['id'], e.get('genre'), e['name'][:44]))
