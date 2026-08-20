"""ジブリパーク展 e+ イベントトップ(4516460001)から全公演の状態を拾う"""
import sys, re, html as H
sys.path.insert(0, r'C:\Users\user\oshinavi\tools')
from eplus_harvest import fetch

url = 'https://eplus.jp/sf/detail/4516460001'
html = fetch(url)
lines = ['=== ' + url, 'len=%d' % len(html)]
hits = sorted(set(re.findall(r'/sf/detail/4516460001-P[0-9A-Za-z]+', html)))
lines.append('公演リンク %d件' % len(hits))
lines += ['  https://eplus.jp' + h for h in hits]
txt = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', H.unescape(html)))
i = txt.find('ジブリパーク展')
lines.append('--- 本文抜粋 ---')
lines.append(txt[max(0, i - 300): i + 4000] if i >= 0 else txt[:3000])
open(r'C:\Users\user\oshinavi\tmp\e40_top.txt', 'w', encoding='utf-8').write('\n'.join(lines))
print('done')
