# -*- coding: utf-8 -*-
"""名前で引いて、そのエントリの枠を全部出す（並び順の相談用）。

🚨並び順ロジックは触らない＝症状の原因はたいてい枠の中身
   （[[feedback_display_order]]／[[feedback_check_existing_logic]]）。
使い方: python tmp/look_entry_0910.py 逃げろお嬢さん
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
KW = sys.argv[1]

h = io.open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))

for e in EVENTS:
    blob = '%s %s' % (e.get('artist') or '', e.get('name') or '')
    if KW not in blob:
        continue
    print('## id=%d  artist=%s' % (e['id'], e.get('artist')))
    print('   name      : %s' % e.get('name'))
    print('   genre     : %s' % e.get('genre'))
    print('   date      : %s' % e.get('date'))
    print('   dateLabel : %s' % e.get('dateLabel'))
    print('   venue     : %s' % e.get('venue'))
    print('   xPost     : %s' % e.get('xPost'))
    print('   枠 %d件' % len(e.get('tickets') or []))
    for t in e.get('tickets') or []:
        print('     type      : %s' % t.get('type'))
        print('       startDate=%s  date(締切)=%s  soldout=%s  saleUntilSoldOut=%s'
              % (t.get('startDate'), t.get('date'), t.get('soldout'),
                 t.get('saleUntilSoldOut')))
        if t.get('dateLabel'):
            print('       dateLabel=%s' % t.get('dateLabel'))
        if t.get('url'):
            print('       url=%s' % t.get('url'))
    print()
