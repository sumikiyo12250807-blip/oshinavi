# -*- coding: utf-8 -*-
"""畳み先を目で決めるための材料を出す（2026-09-16 夜）。
①佐野元春の既存3件（3117/7113/7114）の中身＝どこに畳むか決める
②イルカ11062・Juice=Juice11049 の組み立て結果の枠を全部＝候補の公演が入っているか
③名曲コンサート id7907 の中身＝別主催の公演を混ぜてよいエントリなのか
使い方: python tmp/x0917/inspect_fold2.py
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

src = io.open('index.html', encoding='utf-8').read()
ev = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))}
built = {b['id']: b for b in json.load(io.open('tmp/x0917/built2.json', encoding='utf-8'))}

print('=== 登録側 ===')
for i in (3117, 7113, 7114, 620, 4538, 7907):
    e = ev.get(i)
    if not e:
        print('id%-6s ない' % i)
        continue
    print('id%-6s %s ｜ %s ｜ 枠%d' % (i, e.get('artist'), e.get('genre'), len(e.get('tickets') or [])))
    for t in (e.get('tickets') or []):
        print('        %s%s' % (t.get('type'), ' [売切]' if t.get('soldout') else ''))

print('\n=== 組み立て側 ===')
for i in (11049, 11052, 11062, 11066, 11072, 11073, 11074, 11075, 11077):
    b = built.get(i)
    if not b:
        continue
    print('new%-6s %s ｜ %s' % (i, b.get('artist'), b.get('name') or ''))
    for t in (b.get('tickets') or []):
        print('        %s ｜ %s' % (t.get('type'), (t.get('url') or '')[-28:]))
