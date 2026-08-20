# -*- coding: utf-8 -*-
"""0件と判定されたクエリの実HTMLを検分（CAPTCHA/bot判定でないかを確かめる）"""
import io, re, time, urllib.parse, urllib.request

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/120 Safari/537.36',
    'Accept-Language': 'ja,en;q=0.8',
}

def get(kw, srs=True):
    u = 'https://www.amazon.co.jp/s?k=' + urllib.parse.quote(kw + ' CD') + '&i=specialty-aps'
    if srs:
        u += '&srs=26200021051'
    req = urllib.request.Request(u, headers=HEADERS)
    return u, urllib.request.urlopen(req, timeout=25).read().decode('utf-8', 'replace')

out = []
for kw, srs in [('辻彩奈', True), ('辻彩奈', False), ('岩崎宏美', True)]:
    u, h = get(kw, srs)
    asin = len(set(re.findall(r'data-asin="([A-Z0-9]{10})"', h)))
    out.append('=== k=%s CD  srs=%s' % (kw, srs))
    out.append('   %s' % u)
    out.append('   len=%d  data-asin=%d' % (len(h), asin))
    for mark in ('ロボットではありません', 'api-services-support@amazon.com', 'CAPTCHA',
                 '検索結果', '件の結果', 'に一致する商品はありませんでした',
                 '該当する商品はありません', 'キーワードで検索してみてください',
                 's-search-results', 'srs-breadcrumb'):
        out.append('   [%s] %s' % (mark, mark in h))
    m = re.search(r'([0-9,]+)\s*件(?:以上)?の結果', h)
    out.append('   件数表記: %s' % (m.group(0) if m else 'なし'))
    # 商品タイトルの先頭3件
    titles = re.findall(r'<span class="a-size-(?:base|medium)-plus[^"]*">([^<]{4,60})</span>', h)[:3]
    out.append('   タイトル例: %s' % titles)
    out.append('')
    time.sleep(3)

io.open('tmp/out_amazon_inspect.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('wrote tmp/out_amazon_inspect.txt')
