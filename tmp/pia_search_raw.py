# -*- coding: utf-8 -*-
"""ぴあ検索ページの生HTMLをそのまま保存して構造を確認する（0件だった原因調査用）。"""
import os, sys, time, urllib.parse, urllib.request

UA = {'User-Agent': 'Mozilla/5.0'}
KW = sys.argv[1] if len(sys.argv) > 1 else 'マカロニえんぴつ'
url = 'https://t.pia.jp/pia/search_all.do?kw=%s' % urllib.parse.quote(KW)
html = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode('utf-8', 'replace')
p = os.path.join(os.path.dirname(__file__), 'pia_search_raw.html')
open(p, 'w', encoding='utf-8').write(html)
print('wrote %s (%d bytes)' % (p, len(html)))
print('eventCd count:', html.count('eventCd'))
print('eventBundleCd count:', html.count('eventBundleCd'))
print('has search_all form:', 'search_all' in html)
