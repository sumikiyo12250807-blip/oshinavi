"""e+ の /sf/word/ でジブリパーク展を引き、公演URLを列挙する"""
import sys, re, html as H, urllib.parse
sys.path.insert(0, r'C:\Users\user\oshinavi\tools')
from eplus_harvest import fetch

kw = 'ジブリパーク展'
url = 'https://eplus.jp/sf/word/?keyword=' + urllib.parse.quote(kw)
lines = ['=== ' + url]
try:
    html = fetch(url)
    lines.append('len=%d' % len(html))
    hits = sorted(set(re.findall(r'/sf/detail/[0-9A-Za-z\-]+', html)))
    lines.append('detailリンク %d件' % len(hits))
    lines += ['  https://eplus.jp' + h for h in hits]
    txt = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', H.unescape(html)))
    i = txt.find('ジブリ')
    lines.append('--- 本文抜粋 ---')
    lines.append(txt[max(0, i - 200): i + 3000] if i >= 0 else txt[:2000])
except Exception as ex:
    lines.append('ERROR %r' % (ex,))

open(r'C:\Users\user\oshinavi\tmp\e40_word.txt', 'w', encoding='utf-8').write('\n'.join(lines))
print('done')
