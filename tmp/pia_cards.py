# -*- coding: utf-8 -*-
"""ぴあの1ページから、パーサーが見ているカードをそのまま並べる（状態・券種名・when・飛び先）。"""
import sys, os
os.chdir(r'C:\Users\user\oshinavi')
sys.path.insert(0, 'tools')
from build_pia_entries import fetch, parse_cards, slot_code
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
for u in sys.argv[1:]:
    print('■', u)
    rows = parse_cards(fetch(u))
    print('  カード %d枚' % len(rows))
    for r in rows:
        print('   [%s] %-46s when=%-34s %s' % (
            r['state'], (r['title'] or '')[:46], (r['when'] or '')[:34], slot_code(r.get('url'))))
