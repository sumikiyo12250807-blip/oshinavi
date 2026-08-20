# -*- coding: utf-8 -*-
"""キョードー西日本の玉置浩二ページから、公演ごとの購入リンク（売り場URL）を抽出"""
import io, re, html as H, urllib.request

URL = 'https://www.kyodo-west.co.jp/artist_page.php?a_id=5'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/120 Safari/537.36'}
raw = urllib.request.urlopen(urllib.request.Request(URL, headers=HEADERS), timeout=30).read()
enc = 'utf-8'
m = re.search(rb'charset=["\']?([\w\-]+)', raw[:4000], re.I)
if m:
    enc = m.group(1).decode('ascii', 'ignore')
try:
    h = raw.decode(enc)
except Exception:
    h = raw.decode('utf-8', 'replace')

out = ['encoding=%s len=%d' % (enc, len(h))]

# 公演ブロック＝「■玉置浩二」から次の「■」or末尾まで
blocks = re.split(r'(?=■\s*玉置浩二)', re.sub(r'<!--.*?-->', ' ', h, flags=re.S))
out.append('ブロック数: %d' % len(blocks))
for b in blocks:
    if '玉置浩二' not in b:
        continue
    txt = re.sub(r'\s+', ' ', H.unescape(re.sub(r'<[^>]+>', ' ', b)))
    dm = re.search(r'(20\d\d)/\s*(\d{1,2})/\s*(\d{1,2})\s*\(([^)]*)\)', txt)
    vm = re.search(r'開演\s*([^\s]+(?:\s[^\s]+)?)', txt)
    out.append('--- 公演: %s | %s' % (dm.group(0) if dm else '日付不明',
                                      vm.group(1) if vm else '会場不明'))
    st = re.findall(r'(一般発売|発売中|受付中|発売前|SOLD\s*OUT|完売|予定枚数終了)', txt)
    out.append('    状態語: %s' % sorted(set(st)))
    for am in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', b, re.S):
        href, label = am.group(1), re.sub(r'\s+', ' ', H.unescape(re.sub(r'<[^>]+>', '', am.group(2)))).strip()
        if any(k in label for k in ('購入', 'チケット', '発売', '申込')) or \
           any(k in href for k in ('pia', 'l-tike', 'eplus', 'ticket')):
            out.append('    [link] %s → %s' % (label[:30], href[:160]))

io.open('tmp/out_tamaki_buylinks.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('wrote tmp/out_tamaki_buylinks.txt')
