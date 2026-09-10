# -*- coding: utf-8 -*-
"""主役枠3組の素材を index.html から機械で出す（2026-09-11 発売分）。

主役＝なとり／野村萬斎／春風亭昇太。
台本 X_SCRIPT.md ＝主役枠は「公式サイトも少し見て文章を厚くする」「裏が取れたことだけ書く」。
ここでは**うちのデータに入っている事実だけ**を出す。公式で足すのは別途。
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

NAMES = ['なとり', '野村萬斎', '春風亭昇太']

h = io.open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))

for nm in NAMES:
    print('=' * 74)
    print('■ %s' % nm)
    for e in EVENTS:
        if e.get('genre') == 'new':
            continue
        if nm not in (e.get('artist') or '') + (e.get('name') or ''):
            continue
        print('  id%-5d %s' % (e['id'], e.get('name')))
        print('     artist   : %s' % e.get('artist'))
        print('     dateLabel: %s' % e.get('dateLabel'))
        print('     venue    : %s' % e.get('venue'))
        print('     pref     : %s / 最終公演日 %s / genre %s'
              % (e.get('prefecture'), e.get('date'), e.get('genre')))
        for t in e.get('tickets') or []:
            mark = ''
            if t.get('startDate') == '2026-09-11':
                mark = '  ★明日発売'
            if t.get('soldout'):
                mark += '  【売り切れ】'
            print('     - %-54s date=%s start=%s%s'
                  % ((t.get('type') or '')[:54], t.get('date'), t.get('startDate'), mark))
        print()
