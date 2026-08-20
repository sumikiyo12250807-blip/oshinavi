# -*- coding: utf-8 -*-
"""指定エントリの tickets を見て、画面に「予定枚数終了」で出る枠があるか確かめる。"""
import re, json, io, sys, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
TODAY = datetime.date.today().isoformat()
h = open('index.html', encoding='utf-8', newline='').read()
EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
for i in [int(x) for x in sys.argv[1].split(',')]:
    e = next((x for x in EV if x['id'] == i), None)
    if not e:
        print('id=%d 無い' % i); continue
    vis = '出る' if (e.get('date') or '') >= TODAY else '公演日超過で出ない'
    print('\n=== id=%d %s / 公演日=%s → カード:%s' % (i, e.get('artist', ''), e.get('date'), vis))
    for t in e.get('tickets') or []:
        print('   %s %s | %s' % ('🈵予定枚数終了' if t.get('soldout') else '　　　　　　', t.get('date'), t.get('type')))
