# -*- coding: utf-8 -*-
"""ぴあの任意URLを1回だけ取り、「pia.jp/v/」「特別先行」「プレイガイド先行」「抽選先行」の周辺を表示（読むだけ）。
使い方: python tmp/probe_tokubetsu2_0911.py <url> <保存名>
"""
import re, sys, urllib.request
sys.stdout.reconfigure(encoding='utf-8')
url, name = sys.argv[1], sys.argv[2]
h = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30).read().decode('utf-8', 'replace')
open('tmp/probe_%s.html' % name, 'w', encoding='utf-8').write(h)
print('len', len(h))
for pat in [r'pia\.jp/v/', r'特別先行', r'プレイガイド先行', r'抽選先行']:
    for m in list(re.finditer(pat, h))[:4]:
        s = max(0, m.start() - 400)
        txt = re.sub(r'<[^>]+>', ' ', h[s:m.end() + 400])
        print('--- [%s]' % pat, re.sub(r'\s+', ' ', txt))
