# -*- coding: utf-8 -*-
"""3117 佐野元春&THE COYOTE BAND「一般発売（宮城 10/16公演）〜9/30 23:59」に売り切れの印（2026-09-16 夜）。

根拠＝ぴあの宮城のページ（eventCd=2622925）の生の文言に
  [予定枚数終了] is-active … 2026/10/16(金) 東京エレクトロンホール宮城 ( 宮城県 )
が2回出る（ほかは抽選受付終了2枚と販売終了1枚）。
reconcile が STALE（買える枠に無い）と言ったのは売り切れたから。
🚨「販売終了」に倒すと売り切れを別の事実に書き換える嘘になる（2026-08-14の事故と同じ型）＝soldout だけを付ける。
使い方: python tmp/x0917/mark_sold_3117.py [--apply]
"""
import io
import json
import re
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')
P = 'index.html'
TODAY = '2026-09-16'
ID = 3117
TY = '一般発売（宮城 10/16公演）〜9/30 23:59'

src = io.open(P, encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
e = next(x for x in events if x['id'] == ID)
hit = [t for t in e['tickets'] if t['type'] == TY]
assert len(hit) == 1, [t['type'] for t in e['tickets']]
t = hit[0]
assert not t.get('soldout') and not t.get('saleEnded'), t
t['soldout'] = True
t['soldoutSince'] = TODAY
print('id%d %s -> soldout' % (ID, TY))
if '--apply' in sys.argv:
    shutil.copyfile(P, 'index.html.bak_0916_sold3117')
    out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', '\r\n') + m.group(3) + src[m.end():]
    io.open(P, 'w', encoding='utf-8', newline='').write(out)
    print('wrote')
