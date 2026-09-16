# -*- coding: utf-8 -*-
"""3879 カキンツハルカ「一般発売（東京 R9年 1/13〜1/14公演）〜1/13 23:59」に売り切れの印（2026-09-16 夜）。

根拠＝ぴあのまとめページ b2670158 の生の文言（tmp/pia_statustext.txt）に
  [予定枚数終了] is-active … ～ 2027/1/14(木) ＬＩＮＥ ＣＵＢＥ ＳＨＩＢＵＹＡ ( 東京都 )
が2回出る。reconcile が STALE（買える枠に無い）と言ったのは売り切れたからで、締切切れではない。
売り切れは消さない＝「予定枚数終了」で出し続ける。
使い方: python tmp/x0917/mark_sold_3879.py [--apply]
"""
import io
import json
import re
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')
P = 'index.html'
TODAY = '2026-09-16'
ID = 3879
TY = '一般発売（東京 R9年 1/13〜1/14公演）〜1/13 23:59'

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
    shutil.copyfile(P, 'index.html.bak_0916_sold3879')
    out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', '\r\n') + m.group(3) + src[m.end():]
    io.open(P, 'w', encoding='utf-8', newline='').write(out)
    print('wrote')
