"""e+ の販売窓を機械パースして UTF-8 ファイルに出す"""
import sys
sys.path.insert(0, r'C:\Users\user\oshinavi\tools')
from eplus_harvest import fetch
from reconcile_eplus import parse_blocks

urls = sys.argv[1:]
lines = []
for u in urls:
    lines.append('=== ' + u)
    try:
        html = fetch(u)
        blocks = parse_blocks(html)
        if not blocks:
            lines.append('  (block-ticket 無し)')
        for b in blocks:
            lines.append('  [%s] %s %s 〜 %s %s' % (b['status'], b['sd'], b['st'], b['ed'], b['et']))
    except Exception as ex:
        lines.append('  ERROR %r' % (ex,))

open(r'C:\Users\user\oshinavi\tmp\eplus_peek_0802.txt', 'w', encoding='utf-8').write('\n'.join(lines))
print('wrote', len(urls))
