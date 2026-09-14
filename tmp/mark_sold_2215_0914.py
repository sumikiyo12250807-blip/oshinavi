# -*- coding: utf-8 -*-
"""照合し直しで残った2枠に売り切れの印（2026-09-14 夜・ぴあの生の行＝tmp/raw_rows_2133_0914.md）。消さない。
・9384 ピクサーの世界展＝9/22(火・祝)入場分が予定枚数終了
・9007 ジャイアンツ ファーム＝9/19〜9/20（対西武）が予定枚数終了
（1028 桂宮治の宮城は混雑ページだっただけ＝読み直して一致・直すものなし）
使い方: python tmp/mark_sold_2215_0914.py [--apply]
"""
import datetime
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
MARKS = {9384: '一般発売[9/22(火・祝)入場分]（東京 9/22公演）〜9/21 23:59',
         9007: '一般発売（東京 9/19〜9/20公演）〜9/20 15:30'}
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
by = {e['id']: e for e in events}
for i, ty in MARKS.items():
    hit = [t for t in by[i]['tickets'] if t.get('type') == ty]
    assert len(hit) == 1, 'id%s の枠が1つに決まらない: %s' % (i, ty)
    hit[0]['soldout'] = True
    hit[0]['soldoutSince'] = TODAY
    print('✅ id%s %s ｜%s' % (i, by[i]['name'][:24], ty))
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('書き込み完了')
