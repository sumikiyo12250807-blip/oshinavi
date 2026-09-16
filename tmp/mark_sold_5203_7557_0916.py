# -*- coding: utf-8 -*-
"""5203 -KAN- 木村和 作品展／7557 映画『ファーストボイス』舞台挨拶付き有料先行上映＝今日10:00発売の枠に「予定枚数終了」の印（2026-09-16 昼）。
tools/pia_mark_soldout_slots.py はこの2件を「販売終了」に倒した（同じ公演日に抽選受付終了のカードが混ざる＝弱いほうに倒す作り）。
ぴあの券種の文言は確かめてある＝
  5203 「一般発売 ／ －ＫＡＮ－ 木村和 作品展」＝予定枚数終了
  7557 「一般発売 ／ 映画『ファーストボイス』舞台挨拶付き有料先行上映」＝予定枚数終了
売り切れを「販売終了」と書くのは別の嘘（2026-08-14 の事故と同じ型）なので、証拠どおり soldout だけを付ける。
使い方: python tmp/mark_sold_5203_7557_0916.py [--apply]
"""
import io
import json
import re
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')
P = 'index.html'
TODAY = '2026-09-16'
MARK = {5203: '一般発売（神奈川 11/11公演）9/16 10:00発売',
        7557: '一般発売（大阪 9/23公演）9/16 10:00発売'}

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
    shutil.copyfile(P, 'index.html.bak_0916_sold2')
    out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', '\r\n') + m.group(3) + src[m.end():]
    io.open(P, 'w', encoding='utf-8', newline='').write(out)
    print('書き込んだ')
