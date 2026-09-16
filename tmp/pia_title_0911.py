# -*- coding: utf-8 -*-
"""ぴあの公演ページの正式名（<title> と 公演名の見出し）を出す（読むだけ）。使い方: python tmp/pia_title_0911.py <eventCd> ..."""
import re, sys, time, urllib.request, html
sys.stdout.reconfigure(encoding='utf-8')
for cd in sys.argv[1:]:
    u = 'https://t.pia.jp/pia/event/event.do?eventCd=%s' % cd
    h = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30).read().decode('utf-8', 'replace')
    t = re.search(r'<title>(.*?)</title>', h, re.S)
    sub = re.findall(r'class="[^"]*(?:title|Title)[^"]*"[^>]*>([^<]{4,120})<', h)
    print(cd, '|', html.unescape(t.group(1).strip()) if t else '-')
    for s in sub[:4]:
        print('    ', html.unescape(s.strip()))
    time.sleep(1)
