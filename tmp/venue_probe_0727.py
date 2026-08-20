# -*- coding: utf-8 -*-
"""ぴあ個別ページの生HTMLから会場名がどこに入っているか探す（3286=ナイツで調査）"""
import sys, io, re
sys.path.insert(0, 'tools')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import build_pia_entries as B

h = B.fetch('https://t.pia.jp/pia/event/event.do?eventCd=2626459')
buf = [f'HTML長 {len(h)}']

for kw in ('にじいろホール', '若葉文化ホール', '正和工業'):
    for mm in re.finditer(re.escape(kw), h):
        i = mm.start()
        buf.append(f'\n--- {kw} @ {i} ---')
        buf.append(re.sub(r'\s+', ' ', h[i - 320:i + 160]))
        break

buf.append('\n--- class候補 ---')
for c in sorted(set(re.findall(r'class="([^"]*(?:place|venue|hall|area|kaijo)[^"]*)"', h, re.I))):
    buf.append('   ' + c)

open('tmp/venue_probe.txt', 'w', encoding='utf-8').write('\n'.join(buf))
