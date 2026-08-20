# -*- coding: utf-8 -*-
"""2231 舞台『キュー』の大阪公演の会場・公演日をぴあ生HTMLから取る（結果はUTF-8ファイルへ）"""
import re, io, urllib.request

URL = 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2668891'
req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')

tag = re.compile(r'<[^>]+>')
out = []
out.append('HTML長: %d' % len(html))

for m in re.finditer(r'キュー', html):
    s = max(0, m.start() - 700)
    e = min(len(html), m.end() + 700)
    txt = re.sub(r'\s+', ' ', tag.sub(' ', html[s:e])).strip()
    out.append('=== hit @%d ===' % m.start())
    out.append(txt)
    out.append('')

io.open('tmp/out_2231.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('wrote tmp/out_2231.txt  hits=%d' % len(re.findall(r'キュー', html)))
