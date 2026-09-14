# -*- coding: utf-8 -*-
"""7558 Tommy february6「一般発売（東京・愛知・大阪 10/30〜10/31公演）〜10/30 12:00」＝ぴあ b2670145 の状態欄が「予定枚数終了」
（2026-09-14 昼の照合で STALE・pia_tickets --json の statustext で確認）。消さずに売り切れの印（DELETE_GATE 1.）。
使い方: python tmp/mark_sold_7558_0914.py [--apply]
"""
import datetime
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
e = next(x for x in events if x['id'] == 7558)
hit = [t for t in e['tickets'] if t['type'] == '一般発売（東京・愛知・大阪 10/30〜10/31公演）〜10/30 12:00']
assert len(hit) == 1 and not hit[0].get('soldout'), hit
hit[0]['soldout'] = True
hit[0]['soldoutSince'] = datetime.date.today().isoformat()
print('売り切れの印 id7558 %s' % hit[0]['type'])
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('書き込み完了')
