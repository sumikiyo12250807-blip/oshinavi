# -*- coding: utf-8 -*-
"""楽天のsitemapが「投稿順（新しい公演ほど後ろ）」になっているかを確かめる。

lastmod は当てにならない（27,105件中119件しか動かない）ので、
**並び順そのもの**が新しさの手がかりになるなら、後ろから舐めれば発売前に早く当たる。
"""
import re
import sys

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_perf_status as P

idx = P.fetch('https://ticket.rakuten.co.jp/sitemap.xml')
maps = re.findall(r'<loc>([^<]+)</loc>', idx)
print('サブsitemap %d本' % len(maps))
for m in maps:
    print('   %s' % m)

# 最後のサブsitemapの先頭と末尾を見る
tail = [m for m in maps if 'post-sitemap' in m]
if not tail:
    sys.exit(0)
last = tail[-1]
body = P.fetch(last)
locs = re.findall(r'<loc>([^<]+)</loc>', body)
mods = re.findall(r'<lastmod>([^<]+)</lastmod>', body)
print('\n=== %s  件数=%d' % (last, len(locs)))
for i in list(range(0, 3)) + list(range(max(0, len(locs) - 6), len(locs))):
    print('   [%5d] %-62s %s' % (i, locs[i], mods[i] if i < len(mods) else ''))

first = tail[0]
body2 = P.fetch(first)
locs2 = re.findall(r'<loc>([^<]+)</loc>', body2)
mods2 = re.findall(r'<lastmod>([^<]+)</lastmod>', body2)
print('\n=== %s  件数=%d' % (first, len(locs2)))
for i in list(range(0, 3)) + list(range(max(0, len(locs2) - 3), len(locs2))):
    print('   [%5d] %-62s %s' % (i, locs2[i], mods2[i] if i < len(mods2) else ''))
