# -*- coding: utf-8 -*-
"""push 前の抜き取り（別エージェントがぴあからゼロで読んだ結果）で見つかった売り切れの印のズレを直す（2026-09-16 朝）。
  2477 関西フィル＝9/20（2616693）・12/12（2629798）がぴあで「予定枚数終了」なのに印なし＝買えるフリ → 印を付ける
  4489 ASKA＝熊本 12/26 紙チケットに印があるが、ぴあは「販売期間中 ～ 2026/11/18(水) 23:59」→ 印を外す
使い方: python tmp/fix_pushcheck_0916.py [--apply]
"""
import io
import json
import re
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')
P = 'index.html'
TODAY = '2026-09-16'
MARK = {2477: ['一般発売（大阪 9/20公演）〜9/17 23:59', '一般発売（大阪 12/12公演）〜12/9 23:59']}
UNMARK = {4489: ['一般発売（紙チケット）（熊本 12/26公演）〜11/18 23:59']}

src = io.open(P, encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
n = 0
for e in events:
    for t in e.get('tickets') or []:
        if t.get('type') in MARK.get(e['id'], []):
            assert not t.get('soldout')
            t['soldout'] = True
            t['soldoutSince'] = TODAY
            n += 1
            print('🔴 id%d %s → 予定枚数終了の印' % (e['id'], t['type']))
        if t.get('type') in UNMARK.get(e['id'], []):
            assert t.get('soldout')
            for k in ('soldout', 'soldoutSince', 'saleEnded', 'saleEndedSince'):
                t.pop(k, None)
            n += 1
            print('🟢 id%d %s → 印を外す（ぴあは販売期間中）' % (e['id'], t['type']))
assert n == 3, n
if '--apply' in sys.argv:
    shutil.copyfile(P, 'index.html.bak_0916_pushfix')
    out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', '\r\n') + m.group(3) + src[m.end():]
    io.open(P, 'w', encoding='utf-8', newline='').write(out)
    print('書き込んだ')
