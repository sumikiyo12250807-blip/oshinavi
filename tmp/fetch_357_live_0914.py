# -*- coding: utf-8 -*-
"""35.7 公式サイトの LIVE ページ（1〜3ページ）を生のまま読んで、公演の行（日付＠場所）を機械で拾う（2026-09-14）。
WebFetch に要約させると曜日や会場を作り替える（「2026/11/21(金)」＝実際は土曜）ので、要約を通さない。
使い方: python tmp/fetch_357_live_0914.py
出力: tmp/fetch_357_live_0914.txt
"""
import html
import io
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
rows = []
for n in (1, 2, 3):
    url = 'https://sanjugotennana.com/live/' + ('' if n == 1 else 'page/%d/' % n)
    try:
        h = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode('utf-8', 'replace')
    except Exception as ex:
        rows.append('%s 読めない: %s' % (url, ex))
        continue
    t = html.unescape(re.sub(r'<[^>]+>', '\n', h))
    lines = [re.sub(r'\s+', ' ', x).strip() for x in t.split('\n')]
    lines = [x for x in lines if x]
    for i, x in enumerate(lines):
        if re.search(r'20\d\d[/.]\d{1,2}[/.]\d{1,2}', x):
            ctx = ' ｜ '.join(lines[i:i + 3])
            rows.append('p%d  %s' % (n, ctx[:160]))
io.open('tmp/fetch_357_live_0914.txt', 'w', encoding='utf-8').write('\n'.join(rows) + '\n')
print('拾った行 %d → tmp/fetch_357_live_0914.txt' % len(rows))
