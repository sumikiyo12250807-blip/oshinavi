# -*- coding: utf-8 -*-
"""id6364（俺たちの旅）の東京10/29枠に「予定枚数終了」を付ける。
根拠＝ぴあ実ページ b2667117 の券種が予定枚数終了／build_pia_entries の再構築でも
買える枠は埼玉・広島・福岡の3枠のみ（東京は出てこない）。
売り切れは消さずに出し続ける（memory: feedback_soldout_keep_visible / feedback_saleended_vs_soldout）。
書き戻しは EVENTS 配列の置換のみ（CRLFを壊さない・heal_stale_deadlines と同じ方式）。
"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TODAY = '2026-09-03'
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

hit = 0
for e in EVENTS:
    if e.get('id') != 6364:
        continue
    for t in e.get('tickets', []):
        if '東京 10/29公演' in (t.get('type') or ''):
            t['soldout'] = True
            t['soldoutSince'] = TODAY
            hit += 1
            print('付けた:', t.get('type'))

if hit != 1:
    print('!! 想定と違う（hit=%d）。書き戻さない。' % hit)
    sys.exit(1)

open('index.html.bak_0903_soldout6364', 'w', encoding='utf-8').write(h)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print('書き戻し完了')
