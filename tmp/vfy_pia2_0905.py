# -*- coding: utf-8 -*-
"""保存済みぴあHTMLから ticketSalesList-2024 カードを自力で抜く。"""
import re, io, sys
import html as H
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def txt(x):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', H.unescape(x))).strip()

lines = []
for eid in (583, 6944, 6295, 6080, 6103):
    p = r'C:\Users\user\oshinavi\tmp\vfy_html_0905\pia_%s.html' % eid
    h = io.open(p, encoding='utf-8').read()
    lines.append('##### id=%s' % eid)
    n = 0
    for it in re.split(r'(?=<li class="ticketSalesList-2024__item)', h):
        if 'ticketSalesCard-2024__status' not in it:
            continue
        n += 1
        dts = re.findall(r'datetime="(\d{4}-\d{2}-\d{2}[^"]*)"', it)
        stat = re.search(r'__status (is-[\w-]+)">(.*?)(?:<br|</p>)', it, re.S)
        cls = stat.group(1) if stat else ''
        stt = txt(stat.group(2)) if stat else ''
        when = re.search(r'__status[^>]*>.*?<br>\s*<span[^>]*>(.*?)</span>', it, re.S)
        title = re.search(r'__title">(.*?)</p>', it, re.S)
        places = [txt(x) for x in re.findall(r'__place"[^>]*>(.*?)</span>', it, re.S)]
        region = re.search(r'__region">(.*?)</span>', it, re.S)
        href = re.findall(r'href="([^"]*ticketInformation[^"]*)"', it)
        lines.append('  CARD%d: perf=%s | cls=%s | status=%s | when=%s' % (
            n, dts, cls, stt, txt(when.group(1)) if when else ''))
        lines.append('          title=%s | region=%s | places=%s' % (
            txt(title.group(1)) if title else '', txt(region.group(1)) if region else '', places))
        lines.append('          href=%s' % (href[0] if href else ''))
    if n == 0:
        lines.append('  (ticketSalesCardが0件)')
    lines.append('')

io.open(r'C:\Users\user\oshinavi\tmp\vfy_pia2_0905.txt', 'w', encoding='utf-8').write('\n'.join(lines))
print('ok')
