# -*- coding: utf-8 -*-
"""e+の公演ページにジャンル表記があるか探す。"""
import re, io, urllib.request, html as H
url = 'https://eplus.jp/sf/detail/4590340001-P0030001P021001'
h = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30).read().decode('utf-8', 'replace')
out = io.open('tmp/eplus_genre_probe_0905.txt', 'w', encoding='utf-8')
for pat in [r'genre[^>]{0,80}', r'ジャンル[^<]{0,60}', r'breadcrumb.{0,400}', r'"category"[^,]{0,80}',
            r'data-genre="[^"]*"', r'/sf/word/[^"\']{0,60}']:
    ms = re.findall(pat, h, re.S | re.I)
    out.write('=== %s === %d件\n' % (pat, len(ms)))
    for m in ms[:6]:
        out.write('   ' + H.unescape(re.sub(r'<[^>]+>', ' ', m))[:200].replace('\n', ' ') + '\n')
out.close()
print('OK')
