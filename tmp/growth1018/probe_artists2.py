# -*- coding: utf-8 -*-
import re, sys, urllib.request
sys.stdout.reconfigure(encoding='utf-8')
UA = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
get = lambda u: urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': UA}), timeout=60).read().decode('utf-8', 'replace')
h = get('https://oshinavi.jp/artists.html')
i = h.find('<body')
print('BODY:', h[i:i + 1500])
print('a href 例:', re.findall(r'<a [^>]{0,120}', h)[:8])
print('artist 文字の出現:', len(re.findall(r'artist', h)))
t = get('https://oshinavi.jp/')
for kw in ['artists', 'アーティスト一覧', 'アーティストから']:
    j = t.find(kw)
    print(kw, j, t[max(0, j - 200):j + 100].replace('\n', ' ') if j >= 0 else '')
