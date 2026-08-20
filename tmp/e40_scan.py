"""ジブリパーク展 大阪(e+) の枝番ページを総ざらいして生きた窓を探す"""
import sys, re, html as H
sys.path.insert(0, r'C:\Users\user\oshinavi\tools')
from eplus_harvest import fetch

BASE = 'https://eplus.jp/sf/detail/4516460001-P0030050P0210%02d'
lines = []
for n in range(1, 31):
    url = BASE % n
    try:
        html = fetch(url)
    except Exception as ex:
        lines.append('%s  -> %s' % (url, ex))
        continue
    title = re.search(r'<title>(.*?)</title>', html, re.S)
    t = re.sub(r'\s+', ' ', H.unescape(title.group(1))).strip() if title else ''
    blocks = []
    for s in re.split(r'(?=<section class="block-ticket">)', html):
        if not s.startswith('<section class="block-ticket">'):
            continue
        body = s.split('</section>', 1)[0]
        txt = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', H.unescape(body))).strip()
        blocks.append(txt[:200])
    lines.append('%s | %s' % (url, t))
    for b in blocks:
        lines.append('    ' + b)

open(r'C:\Users\user\oshinavi\tmp\e40_scan.txt', 'w', encoding='utf-8').write('\n'.join(lines))
print('done')
