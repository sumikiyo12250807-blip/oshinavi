# -*- coding: utf-8 -*-
"""アーティストページの生HTMLを保存し、公演一覧がどこから来ているか(API/JSON/別URL)を探る。"""
import os, re, sys, urllib.request

UA = {'User-Agent': 'Mozilla/5.0'}
ACD = sys.argv[1] if len(sys.argv) > 1 else 'E7010019'
url = 'https://t.pia.jp/pia/artist/artists.do?artistsCd=%s' % ACD
html = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode('utf-8', 'replace')
p = os.path.join(os.path.dirname(__file__), 'pia_artist_raw.html')
open(p, 'w', encoding='utf-8').write(html)
print('wrote %s (%d bytes)' % (p, len(html)))
for pat in ['eventCd', 'event.do', '.do?', 'json', 'ajax', 'fetch(', 'XMLHttpRequest', 'releaseInfo', 'rlsInfo', 'api']:
    print('%-16s %d' % (pat, html.count(pat)))
print('--- .do を含むURL（上位30・重複除去）---')
for u in sorted(set(re.findall(r'["\'](/[^"\']*?\.do[^"\']*)["\']', html)))[:30]:
    print(' ', u)
