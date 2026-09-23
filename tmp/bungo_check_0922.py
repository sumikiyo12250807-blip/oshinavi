# -*- coding: utf-8 -*-
"""文豪LETTERS 10月公演の会場と個別eventCdを、ぴあのまとめページから機械で確かめる。"""
import re, sys, html, urllib.request
sys.stdout.reconfigure(encoding='utf-8')
u = 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2670721'
t = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30).read().decode('utf-8', 'replace')
plain = html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', t)))
i = plain.find('2026/10/7')
seg = plain[i:i + 120]
print('10月公演の近く＝北とぴあ ドームホール:', '北とぴあ ドームホール' in seg, '／東京都:', '東京都' in seg)
print('販売期間中 〜2026/10/4 23:59:', '2026/10/4' in seg and '23:59' in seg)
cds = sorted(set(re.findall(r'eventCd=(\d+)', t)))
print('eventCd候補:', cds)
for cd in cds:
    j = t.find('eventCd=' + cd)
    near = html.unescape(re.sub(r'<[^>]+>', ' ', t[max(0, j - 1500):j]))
    print(cd, '直前に2026/10/7あり:', '2026/10/7' in near, '／9/21あり:', '2026/9/21' in near)
