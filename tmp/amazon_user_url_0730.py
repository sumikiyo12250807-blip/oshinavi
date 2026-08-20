# -*- coding: utf-8 -*-
"""ユーザー提示URL（神奈川フィルハーモニー管弦楽団・CD語なし）の中身を見る"""
import io, re, html as H, urllib.request

URL = ('https://www.amazon.co.jp/s?k=%E7%A5%9E%E5%A5%88%E5%B7%9D%E3%83%95%E3%82%A3%E3%83%AB'
       '%E3%83%8F%E3%83%BC%E3%83%A2%E3%83%8B%E3%83%BC%E7%AE%A1%E5%BC%A6%E6%A5%BD%E5%9B%A3'
       '&i=specialty-aps&srs=26200021051&__mk_ja_JP=%E3%82%AB%E3%82%BF%E3%82%AB%E3%83%8A'
       '&crid=2VEHFHQ3UIEGI&ref=nb_sb_noss_1')
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/120 Safari/537.36',
           'Accept-Language': 'ja,en;q=0.8'}
h = urllib.request.urlopen(urllib.request.Request(URL, headers=HEADERS), timeout=30)\
    .read().decode('utf-8', 'replace')

out = ['len=%d' % len(h)]
out.append('data-asin ユニーク数: %d' % len(set(re.findall(r'data-asin="([A-Z0-9]{10})"', h))))
m = re.search(r'([0-9,]+)\s*件(?:以上)?の結果', h)
out.append('件数表記: %s' % (m.group(0) if m else 'なし'))
for mark in ('に一致する商品はありませんでした', '該当する商品はありません',
             'ロボットではありません', 'CAPTCHA'):
    out.append('[%s] %s' % (mark, mark in h))

# 商品タイトルを広めに拾う
titles = re.findall(r'<h2[^>]*>.*?<span[^>]*>([^<]{4,120})</span>', h, re.S)
if not titles:
    titles = re.findall(r'"title"\s*:\s*"([^"]{4,120})"', h)
out.append('--- 商品タイトル（上位15件）')
seen = []
for t in titles:
    t = H.unescape(re.sub(r'\s+', ' ', t)).strip()
    if t and t not in seen:
        seen.append(t)
    if len(seen) >= 15:
        break
out += ['  %d. %s' % (i + 1, t) for i, t in enumerate(seen)]

io.open('tmp/out_amazon_user_url.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('wrote tmp/out_amazon_user_url.txt')
