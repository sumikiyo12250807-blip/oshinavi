# -*- coding: utf-8 -*-
"""ローチケ/主催直販ページを生HTMLで取れるか調べる（WebFetchはECONNRESETで落ちる）。"""
import urllib.request, re, sys
sys.stdout.reconfigure(encoding='utf-8')

URLS = [
    'https://l-tike.com/doc2026/',
    'https://www.stv.jp/event/disney_onclassic/index.html',
    'https://www.akt.co.jp/events/doc2026',
    'https://www.rbc.co.jp/event/event_information/mn2026col/',
]
for u in URLS:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        h = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')
        print(f'\n=== OK {u} / {len(h)}文字')
        for kw in ('発売', '受付', '締切', 'l-tike', 'ローソン', 'プレイガイド'):
            print(f'   「{kw}」{h.count(kw)}回')
        # 日付らしき表記を拾う
        ds = re.findall(r'\d{1,2}月\d{1,2}日[（(][^）)]{1,3}[）)]\s*\d{0,2}:?\d{0,2}', h)
        print('   日付表記サンプル:', ds[:10])
    except Exception as ex:
        print(f'\n=== NG {u} → {type(ex).__name__}: {str(ex)[:60]}')
