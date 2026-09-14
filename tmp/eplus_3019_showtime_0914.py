# -*- coding: utf-8 -*-
"""3019 山本達彦の 9/12 分の配信ページ2本は、題に昼/夜が書いていない。ページの中の「開演」「昼公演」「夜公演」
「アーカイブ」「配信」の前後を拾って、どちらが何時の回かを確かめる（読むだけ・推測で割り当てない）。
使い方: python tmp/eplus_3019_showtime_0914.py
"""
import re
import sys
import time

sys.path.insert(0, 'tools')
import eplus_harvest as eh

sys.stdout.reconfigure(encoding='utf-8')
for u in ('https://eplus.jp/sf/detail/4530900001-P0030001P021002',
          'https://eplus.jp/sf/detail/4530920001-P0030001P021001',
          'https://eplus.jp/sf/detail/4530940001-P0030001P021001'):
    print('=== %s' % u)
    t = eh._flat(re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', eh.fetch(u), flags=re.S))
    seen = set()
    for mm in re.finditer(r'開演|開場|昼公演|夜公演|アーカイブ|視聴期間|配信開始', t):
        s = t[max(0, mm.start() - 40): mm.end() + 60]
        if s in seen:
            continue
        seen.add(s)
        print('  …%s…' % s)
        if len(seen) >= 8:
            break
    time.sleep(1.0)
