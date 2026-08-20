# -*- coding: utf-8 -*-
"""ユーザー提供の amzn.to 短縮リンクの中身を確認（リダイレクト先・並ぶ商品）"""
import io, re, html as H, urllib.parse, urllib.request

URL = 'https://amzn.to/4yOYp4y'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/120 Safari/537.36',
           'Accept-Language': 'ja,en;q=0.8'}
r = urllib.request.urlopen(urllib.request.Request(URL, headers=HEADERS), timeout=30)
h = r.read().decode('utf-8', 'replace')
final = r.geturl()

out = ['短縮元: %s' % URL, '転送先: %s' % final]
q = urllib.parse.parse_qs(urllib.parse.urlparse(final).query)
out.append('パラメータ: %s' % {k: v for k, v in q.items() if k in ('k', 'i', 'srs', 'tag', 'node')})
out.append('data-asin ユニーク数: %d' % len(set(re.findall(r'data-asin="([A-Z0-9]{10})"', h))))
m = re.search(r'([0-9,]+)\s*件(?:以上)?の結果', h)
out.append('件数表記: %s' % (m.group(0) if m else 'なし'))
titles, seen = re.findall(r'<h2[^>]*>.*?<span[^>]*>([^<]{4,120})</span>', h, re.S), []
for t in titles:
    t = H.unescape(re.sub(r'\s+', ' ', t)).strip()
    if t and t not in seen:
        seen.append(t)
    if len(seen) >= 12:
        break
out.append('--- 並ぶもの（上位12）')
out += ['  %d. %s' % (i + 1, t) for i, t in enumerate(seen)]
io.open('tmp/out_amzn_short.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('wrote tmp/out_amzn_short.txt')
