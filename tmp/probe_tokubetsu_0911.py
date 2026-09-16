# -*- coding: utf-8 -*-
"""ぴあの「特別先行（pia.jp/v/ の専用申込ページ）」がイベントページの生HTMLにどう出ているかを見る（読むだけ・1ページだけ叩く）。
使い方: python tmp/probe_tokubetsu_0911.py <eventCd>
"""
import re, sys, urllib.request
sys.stdout.reconfigure(encoding='utf-8')
cd = sys.argv[1]
url = 'https://t.pia.jp/pia/event/event.do?eventCd=%s' % cd
h = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30).read().decode('utf-8', 'replace')
open('tmp/probe_tokubetsu_%s.html' % cd, 'w', encoding='utf-8').write(h)
print('len', len(h), 'sorry' if 'sorry' in h[:3000] else '')
for m in re.finditer(r'pia\.jp/v/[\w\-/]+', h):
    s = max(0, m.start() - 700)
    txt = re.sub(r'<[^>]+>', ' ', h[s:m.end() + 200])
    txt = re.sub(r'\s+', ' ', txt)
    print('---', m.group(0))
    print(txt[-600:])
