# -*- coding: utf-8 -*-
"""A(発売開始)に入れたが券種に「7/9 HH:MM発売」の明示が無い=曖昧なものを洗い出す。
これらは7/9が発売開始か締切か券種から判別不能→ぴあ要確認。"""
import re, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
TARGET = '2026-07-09'
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
for e in EVENTS:
    for t in e.get('tickets', []):
        if t.get('date') != TARGET or '発売' not in t.get('type', ''):
            continue
        typ = t['type']
        if re.search(r'〜\s*7/9', typ):
            break  # B(締切)は対象外
        # 明示的な発売開始形か?
        explicit = re.search(r'7/9\s*\d{1,2}:\d{2}\s*発売', typ)
        if not explicit:
            print('id=%d | %s' % (e['id'], e['artist']))
            print('   type: %s' % typ)
            print('   pia : %s' % e['links'].get('pia'))
            print()
        break
