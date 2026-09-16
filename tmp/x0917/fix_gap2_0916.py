# -*- coding: utf-8 -*-
"""9/17〜9/19発売の突き合わせの続き（2026-09-16 朝）。
① 2648 落合博満の「一般発売（岐阜 9/12〜10/10公演）〜10/7 23:59」＝飛び先が空でまとめページ（b2667481＝岐阜を含まない）に飛ぶ。
   ぴあの実ページ eventCd=2622604 が「販売期間中 ～ 2026/10/7(水) 23:59・岐阜 9/12〜10/10」＝中身は正しいので**飛び先だけ**焼き込む
   （[[feedback_tour_per_ticket_url]]＝押した先に無い枠を作らない）。
② 2207 BRADIO の「一般発売（兵庫 10/4公演）〜9/17 23:59」＝ぴあ eventCd=2617685 で「予定枚数終了」→ 売り切れの印。
   広島の4次プレリザーブは「抽選受付中 ～9/16 11:00」で生きている（登録のまま・触らない）。
使い方: python tmp/x0917/fix_gap2_0916.py [--apply]
"""
import io
import json
import re
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')
P = 'index.html'
TODAY = '2026-09-16'
URLFIX = {2648: [('一般発売（岐阜 9/12〜10/10公演）〜10/7 23:59', 'https://t.pia.jp/pia/event/event.do?eventCd=2622604')]}
MARK = {2207: ['一般発売（兵庫 10/4公演）〜9/17 23:59']}

src = io.open(P, encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
n = 0
for e in events:
    for t in e.get('tickets') or []:
        for ty, url in URLFIX.get(e['id'], []):
            if t.get('type') == ty:
                assert not t.get('url'), t
                t['url'] = url
                n += 1
                print('🔗 id%d %s → 飛び先 %s' % (e['id'], ty[:44], url[-22:]))
        if t.get('type') in MARK.get(e['id'], []):
            assert not t.get('soldout'), t
            t['soldout'] = True
            t['soldoutSince'] = TODAY
            n += 1
            print('🔴 id%d %s → 予定枚数終了の印' % (e['id'], t['type'][:50]))
assert n == 2, n
if '--apply' in sys.argv:
    shutil.copyfile(P, 'index.html.bak_0916_gapfix2')
    out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', '\r\n') + m.group(3) + src[m.end():]
    io.open(P, 'w', encoding='utf-8', newline='').write(out)
    print('書き込んだ')
