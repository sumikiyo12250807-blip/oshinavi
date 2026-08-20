"""ぴあ個別ページの title と本文冒頭を UTF-8 で出す（ジャンル判断用）"""
import sys, re, html as H
sys.path.insert(0, r'C:\Users\user\oshinavi\tools')
from eplus_harvest import fetch

lines = []
for url in sys.argv[1:]:
    lines.append('=== ' + url)
    try:
        h = fetch(url)
        t = re.search(r'<title>(.*?)</title>', h, re.S)
        lines.append('TITLE: ' + (re.sub(r'\s+', ' ', H.unescape(t.group(1))).strip() if t else '-'))
        txt = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', H.unescape(h)))
        i = txt.find('出演')
        lines.append('出演付近: ' + (txt[max(0, i - 100):i + 500] if i >= 0 else '(出演表記なし)'))
    except Exception as ex:
        lines.append('ERROR %r' % (ex,))
open(r'C:\Users\user\oshinavi\tmp\pia_title_0802.txt', 'w', encoding='utf-8').write('\n'.join(lines))
print('ok')
