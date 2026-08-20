"""e+ の block-ticket 生テキスト（ステータス文言まで）を UTF-8 で出す"""
import sys, re, html as H
sys.path.insert(0, r'C:\Users\user\oshinavi\tools')
from eplus_harvest import fetch

url = sys.argv[1]
html = fetch(url)
lines = ['=== ' + url]
for s in re.split(r'(?=<section class="block-ticket">)', html):
    if not s.startswith('<section class="block-ticket">'):
        continue
    body = s.split('</section>', 1)[0]
    txt = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', H.unescape(body))).strip()
    lines.append('--- ' + txt[:600])
open(r'C:\Users\user\oshinavi\tmp\eplus_peek2_0802.txt', 'w', encoding='utf-8').write('\n'.join(lines))
print('blocks', len(lines) - 1)
