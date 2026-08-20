"""ジブリパーク展 大阪：9/5以降の公演コードを総ざらいして受付中の枠を探す"""
import sys, re, html as H
sys.path.insert(0, r'C:\Users\user\oshinavi\tools')
from eplus_harvest import fetch

lines = []
for n in range(45, 80):
    code = 'P00300%02d' % n
    url = 'https://eplus.jp/sf/detail/4516460001-%s' % code
    try:
        html = fetch(url)
    except Exception as ex:
        lines.append('%s -> %s' % (code, ex))
        continue
    ld = re.search(r'"startDate":\s*"([0-9T:\-]+)"', html)
    st = sorted(set(re.findall(r'<span class="ticket-status__item[^"]*">([^<]+)</span>', html)))
    tl = re.search(r'<title>(.*?)</title>', html, re.S)
    lines.append('%s | %s | %s | %s' % (code, ld.group(1) if ld else '-',
                                        ' / '.join(s.strip() for s in st) or '-',
                                        re.sub(r'\s+', ' ', H.unescape(tl.group(1))).strip() if tl else '-'))

open(r'C:\Users\user\oshinavi\tmp\e40_perf.txt', 'w', encoding='utf-8').write('\n'.join(lines))
print('done')
