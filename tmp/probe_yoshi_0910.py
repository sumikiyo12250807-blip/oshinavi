# -*- coding: utf-8 -*-
"""吉幾三の2027年公演が、既存の「吉幾三コンサート 2026」と同じツアーかを見る。"""
import re
import sys

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_perf_status as P   # fetch を借りるだけ

for u in ['https://ticket.pia.jp/pia/event.do?eventCd=2633720',
          'https://t.pia.jp/pia/event/event.do?eventCd=2611801']:
    print('===== %s' % u)
    try:
        body = P.fetch(u)
    except Exception as ex:
        print('  取得失敗 %r\n' % (ex,))
        continue
    t = re.search(r'<title>(.*?)</title>', body, re.S)
    print('  title: %s' % re.sub(r'\s+', ' ', t.group(1))[:150] if t else '  titleなし')
    for kw in ['ツアー', 'TOUR', '2027', '2026']:
        print('    %-6s %d回' % (kw, body.count(kw)))
    print()
