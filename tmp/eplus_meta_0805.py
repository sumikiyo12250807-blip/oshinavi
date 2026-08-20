# -*- coding: utf-8 -*-
"""e+ /sf/detail/ から 公演名・会場・公演日・各枠の受付期間/状態 を機械抽出する。"""
import re, sys, urllib.request, html
sys.stdout.reconfigure(encoding='utf-8')

for url in sys.argv[1:]:
    h = urllib.request.urlopen(
        urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=60
    ).read().decode('utf-8', 'replace')
    print('=' * 70)
    print(url)

    def pick(pat, label):
        for m in re.findall(pat, h, re.S):
            t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', m))).strip()
            if t:
                print('  %s %s' % (label, t[:120]))
                return

    pick(r'<title>(.*?)</title>', 'title:')
    for key in ('koen_name', 'venue_name', 'kaijo_name', 'koen_date', 'kouen_date'):
        s = set(re.findall(r'"%s":"([^"]{1,80})"' % key, h))
        if s:
            print('  %s = %s' % (key, ' / '.join(sorted(s))[:200]))
    # 公演日時らしき表記
    for m in sorted(set(re.findall(r'20\d\d/\d{1,2}/\d{1,2}\([月火水木金土日]\)\s*\d{1,2}:\d{2}', h)))[:6]:
        print('  公演日時候補: %s' % m)
    for blk in re.findall(r'<li[^>]*class="[^"]*ticket-status[^"]*"[^>]*>(.*?)</li>', h, re.S)[:8]:
        t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', blk))).strip()
        if t:
            print('  状態: %s' % t[:80])
