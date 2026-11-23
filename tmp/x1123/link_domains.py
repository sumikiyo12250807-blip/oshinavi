# -*- coding: utf-8 -*-
# サイトのリンク先の住所（ドメイン）を数え、いまの数える決まり（click_track の正規表現）に入らないものを出す
import io, re, collections, sys, glob
sys.path.insert(0, 'C:/Users/user/oshinavi/tools')
import compact_events as C
R = 'C:/Users/user/oshinavi/'
t = io.open(R + 'index.html', encoding='utf-8', newline='').read()
E = C.load(t)
cnt = collections.Counter()
for e in E:
    for u in [x.get('url') for x in e.get('tickets') or []] + list((e.get('links') or {}).values()):
        if isinstance(u, str) and u.startswith('http'):
            cnt[re.match(r'https?://([^/]+)', u).group(1)] += 1
# EVENTS の外（ボタン・バナーを作る JS の中の住所）
s, end, _ = C.locate(t)
rest = t[:s] + t[end:]
for f in glob.glob(R + 'artist/1*.html')[:3]:
    rest += io.open(f, encoding='utf-8').read()
for m in re.finditer(r'https?://([a-z0-9.-]+\.[a-z]{2,})', rest):
    cnt['(画面のコード) ' + m.group(1)] += 1
amazon = re.compile(r'amazon\.co\.jp|amzn\.to'); rak = re.compile(r'linksynergy|ticket\.rakuten')
hotel = re.compile(r'valuecommerce|expedia'); tick = re.compile(r'pia\.jp|eplus\.jp|l-tike|tiget|fany|zaiko|livepocket|yoshimoto|tv-asahi|ticket-web-shochiku')
o = io.open(R + 'tmp/x1123/link_domains.txt', 'w', encoding='utf-8')
for d, n in cnt.most_common():
    k = 'amazon' if amazon.search(d) else 'rakuten' if rak.search(d) else 'hotel' if hotel.search(d) else 'ticket' if tick.search(d) else '★数えていない'
    o.write('%6d %-14s %s\n' % (n, k, d))
