# -*- coding: utf-8 -*-
"""9/16夜のX準備の総ざらいで見つかった売り切れ2枠に印を付ける（2026-09-16）。
ぴあの券種の文言を確かめてある＝
  564 SINON「一般発売（栃木 11/3公演）〜10/18 23:59」＝予定枚数終了（カード2枚）
  702 TSUKEMEN「一般発売（神奈川 10/3公演）〜9/29 23:59」＝予定枚数終了（同じ公演日に抽選受付終了が混ざるので道具は「販売終了」に倒した）
売り切れを「販売終了」と書くのは別の嘘になるので、証拠どおり soldout だけを付ける。
使い方: python tmp/x0917/mark_sold_564_702.py [--apply]
"""
import io
import json
import re
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')
P = 'index.html'
TODAY = '2026-09-16'
MARK = {564: '一般発売（栃木 11/3公演）〜10/18 23:59',
        702: '一般発売（神奈川 10/3公演）〜9/29 23:59'}

src = io.open(P, encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
n = 0
for e in events:
    ty = MARK.get(e['id'])
    if not ty:
        continue
    hit = [t for t in e['tickets'] if t['type'] == ty]
    assert len(hit) == 1, (e['id'], [t['type'] for t in e['tickets']])
    t = hit[0]
    assert not t.get('soldout') and not t.get('saleEnded'), t
    t['soldout'] = True
    t['soldoutSince'] = TODAY
    n += 1
    print('🔴 id%-5s %s → 予定枚数終了の印' % (e['id'], ty))
assert n == 2, n
if '--apply' in sys.argv:
    shutil.copyfile(P, 'index.html.bak_0916_sold564_702')
    out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', '\r\n') + m.group(3) + src[m.end():]
    io.open(P, 'w', encoding='utf-8', newline='').write(out)
    print('書き込んだ')
