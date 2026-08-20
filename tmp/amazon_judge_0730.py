# -*- coding: utf-8 -*-
"""Amazon検索の「0件」判定器を作る。無意味クエリ／確実にある名前で叩いて差分マーカーを探す"""
import io, re, time, urllib.parse, urllib.request

def fetch(kw):
    u = ('https://www.amazon.co.jp/s?k=' + urllib.parse.quote(kw + ' CD')
         + '&i=specialty-aps&srs=26200021051')
    req = urllib.request.Request(u, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/120 Safari/537.36',
        'Accept-Language': 'ja,en;q=0.8'})
    return urllib.request.urlopen(req, timeout=25).read().decode('utf-8', 'replace')

CASES = [
    ('岩崎宏美', 'あるはず'),
    ('ズズゾゾ架空アーティスト名XQZ', '無いはず'),
    ('0歳児からのコンサート', '疑い(企画公演)'),
    ('愛知室内オーケストラ', '団体名のみ'),
]
out = []
for kw, note in CASES:
    try:
        h = fetch(kw)
    except Exception as ex:
        out.append('%s [%s] ❌ %s' % (kw, note, str(ex)[:100]))
        continue
    marks = {
        '該当する商品はありません': '該当する商品はありません' in h,
        'に一致する商品はありませんでした': 'に一致する商品はありませんでした' in h,
        'キーワードを変更': 'キーワードを変更' in h,
        's-no-outline(結果カード)': h.count('s-result-item'),
        'data-asin数': len(set(re.findall(r'data-asin="([A-Z0-9]{10})"', h))),
    }
    out.append('=== %s [%s] len=%d' % (kw, note, len(h)))
    for k, v in marks.items():
        out.append('    %s: %s' % (k, v))
    time.sleep(3)

io.open('tmp/out_amazon_judge.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(out).encode('ascii', 'replace').decode('ascii'))
