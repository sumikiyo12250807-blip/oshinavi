# -*- coding: utf-8 -*-
"""ぴあの生HTMLから公演名まわり（title / h1 / 公演名見出し）だけを抜く。

WebFetchの要約に判断させない（[[feedback_webfetch_soldout_false_positive]]）ための小道具。
"""
import html as _html
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/125.0 Safari/537.36')

for url in sys.argv[1:]:
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    h = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')
    print('=== %s' % url)
    m = re.search(r'<title>(.*?)</title>', h, re.S)
    if m:
        print('  title : %s' % _html.unescape(m.group(1)).strip())
    for tag in ('h1', 'h2'):
        for m in re.finditer(r'<%s[^>]*>(.*?)</%s>' % (tag, tag), h, re.S):
            t = _html.unescape(re.sub(r'<[^>]+>', ' ', m.group(1)))
            t = re.sub(r'\s+', ' ', t).strip()
            if t:
                print('  %-6s: %s' % (tag, t[:120]))
    print()
