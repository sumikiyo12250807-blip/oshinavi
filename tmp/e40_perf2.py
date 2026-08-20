"""ジブリパーク展 大阪：公演コード全域を走査＋受付中窓の受付期間を拾う"""
import sys, re, html as H
sys.path.insert(0, r'C:\Users\user\oshinavi\tools')
from eplus_harvest import fetch

PERIOD = re.compile(r'受付期間\s*[:：]?\s*([0-9]{4})/([0-9]{1,2})/([0-9]{1,2}).{0,6}?([0-9]{1,2}):([0-9]{2})\s*[～~〜]\s*([0-9]{4})/([0-9]{1,2})/([0-9]{1,2}).{0,6}?([0-9]{1,2}):([0-9]{2})')

lines = []
for n in range(1, 46):
    code = 'P00300%02d' % n
    url = 'https://eplus.jp/sf/detail/4516460001-%s' % code
    try:
        html = fetch(url)
    except Exception as ex:
        lines.append('%s -> %s' % (code, ex))
        continue
    ld = re.search(r'"startDate":\s*"([0-9T:\-]+)"', html)
    tl = re.search(r'<title>(.*?)</title>', html, re.S)
    title = re.sub(r'\s+', ' ', H.unescape(tl.group(1))).strip() if tl else '-'
    txt = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', H.unescape(html)))
    per = PERIOD.search(txt)
    st = sorted(set(s.strip() for s in re.findall(r'<span class="ticket-status__item[^"]*">([^<]+)</span>', html)))
    lines.append('%s | %s | %s | %s | %s' % (
        code, ld.group(1) if ld else '-', ' / '.join(st) or '-',
        per.group(0) if per else '受付期間-', title))

open(r'C:\Users\user\oshinavi\tmp\e40_perf2.txt', 'w', encoding='utf-8').write('\n'.join(lines))
print('done')
