# -*- coding: utf-8 -*-
"""新着プール（genre=="new"）の棚卸し。売り場・_genre・_srcgenre の有無を数え、
「機械で決まる分」と「決まらない分」を分けてUTF-8のレポートに書く（2026-09-23 夜）。
🚨[[feedback_genre_pia_asis_and_other]]＝売り場の言う通りに写す。出していないものは推測しない。
使い方: python tmp/x0923/newpool_stats.py
"""
import collections
import io
import json
import re

text = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
events, _ = json.JSONDecoder().raw_decode(text, m.start(1))

pool = [e for e in events if e.get('genre') == 'new']


def vendor(e):
    links = e.get('links') or {}
    for k in ('tiget', 'zaiko', 'fany', 'eplus', 'rakuten', 'lawson', 'pia'):
        if links.get(k):
            return k
    return '(no-link)'


by_vendor = collections.Counter(vendor(e) for e in pool)
has_g = collections.Counter()
srcg = collections.Counter()
decidable, undecidable = [], []
for e in pool:
    v = vendor(e)
    g = e.get('_genre')
    s = e.get('_srcgenre')
    has_g[(v, bool(g))] += 1
    if s:
        srcg[s] += 1
    (decidable if g else undecidable).append(e)

out = io.open('tmp/x0923/newpool_stats.txt', 'w', encoding='utf-8')
out.write('新着プール 合計 %d件\n\n' % len(pool))
out.write('== 売り場別 ==\n')
for k, c in by_vendor.most_common():
    out.write('  %-10s %4d\n' % (k, c))
out.write('\n== _genre（ビルダーが決めたジャンル）を持つか ==\n')
for (v, b), c in sorted(has_g.items()):
    out.write('  %-10s _genre%s %4d\n' % (v, 'あり' if b else 'なし', c))
out.write('\n機械で決まる（_genreあり） %d件 / 決まらない %d件\n' % (len(decidable), len(undecidable)))

out.write('\n== _genre の内訳 ==\n')
for g, c in collections.Counter(e['_genre'] for e in decidable).most_common():
    out.write('  %-12s %4d\n' % (g, c))

out.write('\n== _srcgenre（売り場の申告）上位 ==\n')
for s, c in srcg.most_common(40):
    out.write('  %-16s %4d\n' % (s, c))

out.write('\n== _genre が無い分の売り場別 ==\n')
for k, c in collections.Counter(vendor(e) for e in undecidable).most_common():
    out.write('  %-10s %4d\n' % (k, c))
out.write('\n== _genre が無い分（先頭60件）==\n')
for e in undecidable[:60]:
    out.write('  id=%-6s %-8s %s\n' % (e['id'], vendor(e), (e.get('name') or e.get('artist') or '')[:44]))
out.close()
print('WROTE tmp/x0923/newpool_stats.txt  pool=%d decidable=%d undecidable=%d'
      % (len(pool), len(decidable), len(undecidable)))
