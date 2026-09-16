# -*- coding: utf-8 -*-
"""9/17〜9/19発売の突き合わせで見つかった直し（2026-09-16 朝の空き時間）。
印＝ぴあの実ページで「予定枚数終了」と確かめた2枠
  44   追加販売【注釈付指定席】（沖縄 11/14〜11/15公演）〜11/14 23:59
  2648 一般発売（広島 9/21公演）〜9/20 23:59
会期＝reconcile の QC-EVDATE（今の date だと千秋楽より前＝画面から早く消える）。値はぴあから組み立て直した結果（tmp/x0917/built_dates.json）
  2648 → 2026-11-08（全国ツアー）／4967 → 2027-02-28（東京・宮城・大阪・福岡）
使い方: python tmp/x0917/fix_gap_0916.py [--apply]
"""
import io
import json
import re
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')
P = 'index.html'
TODAY = '2026-09-16'
MARK = {44: ['追加販売【注釈付指定席】（沖縄 11/14〜11/15公演）〜11/14 23:59'],
        2648: ['一般発売（広島 9/21公演）〜9/20 23:59']}
built = {b['id']: b for b in json.load(io.open('tmp/x0917/built_dates.json', encoding='utf-8'))}
DATES = {2648: built[990201], 4967: built[990202]}

src = io.open(P, encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
n = 0
for e in events:
    for t in e.get('tickets') or []:
        if t.get('type') in MARK.get(e['id'], []):
            assert not t.get('soldout'), t
            t['soldout'] = True
            t['soldoutSince'] = TODAY
            n += 1
            print('🔴 id%d %s → 予定枚数終了の印' % (e['id'], t['type'][:56]))
    b = DATES.get(e['id'])
    if b:
        assert b['date'] > e['date'], (e['id'], e['date'], b['date'])
        print('📅 id%d 会期 %s → %s ／ 県 %s → %s' % (e['id'], e['dateLabel'], b['dateLabel'], e['prefecture'], b['prefecture']))
        e['date'], e['dateLabel'], e['venue'], e['prefecture'] = b['date'], b['dateLabel'], b['venue'], b['prefecture']
        n += 1
assert n == 4, n
if '--apply' in sys.argv:
    shutil.copyfile(P, 'index.html.bak_0916_gapfix')
    out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', '\r\n') + m.group(3) + src[m.end():]
    io.open(P, 'w', encoding='utf-8', newline='').write(out)
    print('書き込んだ')
