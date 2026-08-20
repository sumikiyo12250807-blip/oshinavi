# -*- coding: utf-8 -*-
"""キョードー西日本ページの「チケットのご購入」周辺の生HTMLを見る"""
import io, re, urllib.request

URL = 'https://www.kyodo-west.co.jp/artist_page.php?a_id=5'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/120 Safari/537.36'}
raw = urllib.request.urlopen(urllib.request.Request(URL, headers=HEADERS), timeout=30).read()
h = raw.decode('shift_jis', 'replace')

out = []
out.append('■ 全 <a href> の一覧')
for m in re.finditer(r'<a[^>]+href="([^"]+)"', h):
    out.append('   %s' % m.group(1))
out.append('')
out.append('■「チケットのご購入」周辺 生HTML')
for m in re.finditer(r'チケットのご購入', h):
    out.append('--- @%d' % m.start())
    out.append(h[max(0, m.start() - 900): m.start() + 300])
    out.append('')
out.append('■「一般発売」周辺 生HTML（先頭2件）')
for m in list(re.finditer(r'一般発売', h))[:2]:
    out.append('--- @%d' % m.start())
    out.append(h[max(0, m.start() - 500): m.start() + 600])
    out.append('')

io.open('tmp/out_tamaki_raw.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('wrote tmp/out_tamaki_raw.txt')
