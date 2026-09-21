# -*- coding: utf-8 -*-
"""「予定枚数終了」のカードに販売期間が書かれているかを実HTMLで見る。
売り切れ枠を取り込むとき、締切をどこから取るか（書いてあるのか／公演日を置き場にするのか）を決めるため。
"""
import io, re, sys

sys.path.insert(0, 'tools')
import build_pia_entries as B

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
h = io.open('tmp/x0921/probe_2621690.html', encoding='utf-8', errors='replace').read()
cards = B.parse_cards(h)
out = io.open('tmp/x0921/pia_soldout_card.txt', 'w', encoding='utf-8')
out.write('カード %d枚\n\n' % len(cards))
for c in cards:
    out.write('state=%-6s when=%r\n  title=%s\n  perfdate=%s perf_end=%s venue=%s\n  url=%s\n\n'
              % (c.get('state'), c.get('when'), (c.get('title') or '')[:60],
                 c.get('perfdate'), c.get('perf_end'), (c.get('venue') or '')[:30],
                 (c.get('url') or '')[:80]))
# 生HTMLの status 文言も並べる
out.write('=== 生HTMLの status 文言 ===\n')
for m in re.finditer(r'__status (is-[\w-]+)">(.*?)(?:<br|</p>)', h, re.S):
    out.write('  %-12s %s\n' % (m.group(1), re.sub(r'<[^>]+>', '', m.group(2)).strip()[:60]))
out.close()
print('wrote tmp/x0921/pia_soldout_card.txt  cards=%d' % len(cards))
