# -*- coding: utf-8 -*-
"""eventCd=2627269 の「ぴあカードで確率UP」「当選確率アップ」が別券種なのか確かめる。

あたしの数え方（ブロックを切って状態語を含む行を並べる）だと、
**販促のラベル**が行の頭に付いただけの同じ枠を2行に見せる可能性がある。
だから **その文字列の近くにある lotRlsCd/rlsCd** を見て、売り場が別かどうかで決める。
"""
import re, io, html as H, http.client

URL = 'https://t.pia.jp/pia/event/event.do?eventCd=2627269'
path = URL.split('t.pia.jp', 1)[1]
conn = http.client.HTTPSConnection('t.pia.jp', timeout=40)
conn.request('GET', path, headers={'User-Agent': 'Mozilla/5.0', 'Accept-Encoding': 'identity'})
raw = conn.getresponse().read().decode('utf-8', 'replace')
conn.close()

out = io.open('tmp/check_2627269_0905.txt', 'w', encoding='utf-8')
out.write('%s\n混雑ページ=%s / 長さ=%d\n\n' % (URL, ('大変混み合' in raw), len(raw)))

for kw in ('ぴあカードで確率UP', '当選確率アップ', '3次受付'):
    hits = [m.start() for m in re.finditer(re.escape(kw), raw)]
    out.write('■ "%s" は %d か所\n' % (kw, len(hits)))
    for p in hits:
        seg = raw[max(0, p - 900):p + 1800]
        codes = sorted(set(re.findall(r'ticketInformation\.do\?(?:lot)?[Rr]lsCd=(\d+)', seg)))
        txt = H.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', raw[p:p + 260])))
        out.write('   pos=%d 近くの売り場コード=%s\n     %s\n' % (p, codes, txt.strip()[:200]))
    out.write('\n')

allc = sorted(set(re.findall(r'ticketInformation\.do\?(?:lot)?[Rr]lsCd=(\d+)', raw)))
out.write('このページの売り場コード全部 = %s\n' % allc)
out.close()
print('OK codes=%s' % allc)
