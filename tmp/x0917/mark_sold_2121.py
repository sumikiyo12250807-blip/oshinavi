# -*- coding: utf-8 -*-
"""2121 春風亭一之輔独演会「一般発売（神奈川 10/29公演）〜10/26 23:59」に売り切れの印（2026-09-16 夕）。
ぴあの実ページ eventCd=2622417 は状態の文言が「予定枚数終了」2枚だけ＝買える枠は無い（tmp/x0917/statustext_2121.txt）。
tools/pia_mark_soldout_slots.py は判定を出さなかった（券種名と公演日の当て方が合わない形）ので、証拠どおり soldout だけを付ける。
使い方: python tmp/x0917/mark_sold_2121.py [--apply]
"""
import io
import json
import re
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')
P = 'index.html'
TODAY = '2026-09-16'
ID = 2121
TY = '一般発売（神奈川 10/29公演）〜10/26 23:59'

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
print('🔴 id%d %s → 予定枚数終了の印' % (ID, TY))
if '--apply' in sys.argv:
    shutil.copyfile(P, 'index.html.bak_0916_sold2121')
    out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', '\r\n') + m.group(3) + src[m.end():]
    io.open(P, 'w', encoding='utf-8', newline='').write(out)
    print('書き込んだ')
