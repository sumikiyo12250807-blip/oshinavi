# -*- coding: utf-8 -*-
"""soldout枠の現況チェック（表示されているか / 安全弁で消えていないか）。"""
import re, json, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

TODAY = datetime.date.today().isoformat()
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
evs = json.loads(m.group(2))

shown, hidden_by_showdate = [], []
for e in evs:
    so = [t for t in (e.get('tickets') or []) if t.get('soldout')]
    if not so:
        continue
    rec = (e.get('id'), e.get('name') or e.get('artist'), e.get('date'), len(so),
           sorted({t.get('soldoutSince') for t in so}))
    if (e.get('date') or '9999') < TODAY:
        hidden_by_showdate.append(rec)
    else:
        shown.append(rec)

print('TODAY', TODAY)
print('soldoutを持つエントリ数', len(shown) + len(hidden_by_showdate))
print('画面に「予定枚数終了」で出ている', len(shown))
print('公演日を過ぎて非表示(安全弁)', len(hidden_by_showdate))
print('soldout枠の合計', sum(r[3] for r in shown + hidden_by_showdate))
print('--- 表示中(最大15件) ---')
for r in shown[:15]:
    print(r[0], r[1], 'date=', r[2], 'soldout枠=', r[3], r[4])
print('--- 非表示 ---')
for r in hidden_by_showdate:
    print(r[0], r[1], 'date=', r[2], 'soldout枠=', r[3], r[4])

# 全枠soldout=カード自体が「終了」扱いになる子
allso = [e for e in evs
         if (e.get('tickets') and all(t.get('soldout') for t in e['tickets'])
             and (e.get('date') or '9999') >= TODAY)]
print('--- 全枠soldout(カードは残るがカウントダウン無し) ---', len(allso))
for e in allso[:15]:
    print(e.get('id'), e.get('name') or e.get('artist'), e.get('date'))
