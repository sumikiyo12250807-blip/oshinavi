# -*- coding: utf-8 -*-
"""5051 ヤングスキニー「一般発売（熊本 10/23公演）〜10/22 23:59」＝ぴあ eventCd=2633473 は「受付終了」（2026-09-14 昼に pia_tickets --all で確認）。
売り切れ（予定枚数終了）の文言は無い（mark_soldout も「表示なし」）＝裏が取れないので弱いほう＝販売終了に倒す（DELETE_GATE 1.）。
消さない＝soldout:true ＋ saleEnded:true ＋ saleEndedSince。
使い方: python tmp/mark_ended_5051_0914.py [--apply]
"""
import datetime
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
e = next(x for x in events if x['id'] == 5051)
hit = [t for t in e['tickets'] if t['type'] == '一般発売（熊本 10/23公演）〜10/22 23:59' and '2633473' in (t.get('url') or '')]
assert len(hit) == 1, [t['type'] for t in e['tickets']]
t = hit[0]
assert not t.get('soldout'), t
t['soldout'] = True
t['saleEnded'] = True
t['saleEndedSince'] = TODAY
print('販売終了の印 id5051 %s' % t['type'])
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('書き込み完了')
