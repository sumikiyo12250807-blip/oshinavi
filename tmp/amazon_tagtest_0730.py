# -*- coding: utf-8 -*-
"""監査で0件、単独で6件だった差の切り分け：tag= の有無 / 連続アクセスの影響"""
import io, re, time, urllib.parse, urllib.request

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/120 Safari/537.36',
    'Accept-Language': 'ja,en;q=0.8',
}

def get(kw, tag):
    u = ('https://www.amazon.co.jp/s?k=' + urllib.parse.quote(kw + ' CD')
         + '&i=specialty-aps&srs=26200021051')
    if tag:
        u += '&tag=oshinavi0a-22'
    req = urllib.request.Request(u, headers=HEADERS)
    h = urllib.request.urlopen(req, timeout=25).read().decode('utf-8', 'replace')
    return len(set(re.findall(r'data-asin="([A-Z0-9]{10})"', h))), len(h)

out = []
for kw in ('辻彩奈', 'LOLOET', 'MOMO', '神奈川フィルハーモニー管弦楽団'):
    for tag in (True, False):
        try:
            n, ln = get(kw, tag)
            out.append('k=%-22s tag=%-5s → data-asin=%d (len=%d)' % (kw, tag, n, ln))
        except Exception as ex:
            out.append('k=%-22s tag=%-5s → ❌ %s' % (kw, tag, str(ex)[:60]))
        time.sleep(4)

io.open('tmp/out_amazon_tagtest.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(out).encode('ascii', 'replace').decode('ascii'))
