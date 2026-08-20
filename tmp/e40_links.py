"""ジブリパーク展の e+ 詳細ページから他公演へのリンクを洗い出す"""
import sys, re, html as H
sys.path.insert(0, r'C:\Users\user\oshinavi\tools')
from eplus_harvest import fetch

url = 'https://eplus.jp/sf/detail/4516460001-P0030050P021017'
html = fetch(url)
lines = ['=== ' + url, 'len=%d' % len(html)]
hits = sorted(set(re.findall(r'/sf/detail/[0-9A-Za-z\-]+', html)))
lines.append('detailリンク %d件' % len(hits))
lines += ['  https://eplus.jp' + h for h in hits]
others = sorted(set(re.findall(r'https?://[^\s"\'<>]*ghibli[^\s"\'<>]*', html, re.I)))
lines.append('ghibli系リンク %d件' % len(others))
lines += ['  ' + o for o in others[:20]]
# JSON-LD
for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
    lines.append('--- LD ---')
    lines.append(re.sub(r'\s+', ' ', m.group(1))[:1500])
open(r'C:\Users\user\oshinavi\tmp\e40_links.txt', 'w', encoding='utf-8').write('\n'.join(lines))
print('done')
