# -*- coding: utf-8 -*-
"""さだまさしの楽天特設ページから「楽天が扱っている公演」だけを取り出す。

特設ページは**ツアーの全日程**を並べているが、1行ずつ状態が違う:
  SOLD OUT ／ 取り扱いなし ／ 発売中(リンクあり) など。
「取り扱いなし」は**楽天では売っていない**＝楽天リンクを貼ってはいけない行
（[[feedback_vendor_priority]]「そこで売っていないのに楽天リンクを貼らない」）。
"""
import re
import sys

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_perf_status as P

U = 'https://ticket.rakuten.co.jp/features/sada-tour-2026/'
body = P.fetch(U)

# 表の行＝<tr> の中に 日付 / 場所 / 会場 / 開場 / 開演 / 状態
rows = re.findall(r'<tr[^>]*>(.*?)</tr>', body, re.S)
print('表の行 %d' % len(rows))
out = []
for r in rows:
    cells = [P.strip_tags(c) for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, re.S)]
    cells = [c for c in cells if c != '']
    if not cells:
        continue
    d = re.match(r'^(\d{1,2})月(\d{1,2})日', cells[0])
    if not d:
        continue
    href = re.search(r'href="([^"]+)"', r)
    out.append((cells, href.group(1) if href else ''))

import collections
c = collections.Counter()
for cells, href in out:
    state = cells[-1] if cells else ''
    c[state] += 1
print('状態の内訳: %s' % dict(c))
print()
for cells, href in out:
    print('  %-10s %-6s %-30s %-14s %s'
          % (cells[0], cells[1] if len(cells) > 1 else '', (cells[2] if len(cells) > 2 else '')[:30],
             cells[-1][:14], href[:70]))
