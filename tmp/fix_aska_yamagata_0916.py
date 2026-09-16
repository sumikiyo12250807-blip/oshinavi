# -*- coding: utf-8 -*-
"""4489 ASKA 山形 12/13 の電子チケットに売り切れの印を付け直す（2026-09-16 朝）。
pia_mark_soldout_slots が「同じ公演日に紙が受付中」を見て電子の印まで外した（紙と電子を区別しない穴）。
ぴあの実ページ（別エージェントの読み・2610486 rlsCd=010）＝「一般発売（山形／電子チケット）」は 予定枚数終了。紙（rlsCd=004）は販売期間中のまま。
使い方: python tmp/fix_aska_yamagata_0916.py
"""
import io
import json
import re
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')
P = 'index.html'
TY = '一般発売（山形/電子チケット）（山形 12/13公演）〜11/5 23:59'
src = io.open(P, encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
e = next(x for x in events if x['id'] == 4489)
hit = [t for t in e['tickets'] if t['type'] == TY]
assert len(hit) == 1 and not hit[0].get('soldout'), hit
hit[0]['soldout'] = True
hit[0]['soldoutSince'] = '2026-09-16'
shutil.copyfile(P, 'index.html.bak_0916_aska')
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', '\r\n') + m.group(3) + src[m.end():]
io.open(P, 'w', encoding='utf-8', newline='').write(out)
print('🔴 id4489 %s → 予定枚数終了の印' % TY)
