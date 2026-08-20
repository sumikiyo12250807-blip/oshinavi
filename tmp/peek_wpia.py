#!/usr/bin/env python3
"""w.pia.jp 券種ページに販売期間(開始〜終了)があるか確認"""
import io
import re
import sys
import urllib.request
import html as _html

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

for URL in ['https://w.pia.jp/t/nobinobi26-2days/', 'https://w.pia.jp/t/nobinobi26-day1-1/']:
    print('=' * 70)
    print('URL:', URL)
    try:
        req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=60) as r:
            print('HTTP', r.status)
            html = r.read().decode('utf-8', 'replace')
    except Exception as e:
        print('取得失敗:', e)
        continue

    m = re.search(r'<title>(.*?)</title>', html, re.S)
    print('title:', (m.group(1).strip() if m else '無し'))

    txt = re.sub(r'<script.*?</script>', '', html, flags=re.S)
    txt = re.sub(r'<style.*?</style>', '', txt, flags=re.S)
    txt = re.sub(r'<[^>]+>', ' ', txt)
    txt = _html.unescape(re.sub(r'\s+', ' ', txt)).strip()

    for kw in ['受付期間', '販売期間', '発売', '受付中', '受付終了', '予定枚数', '完売', '申込']:
        if kw in txt:
            print(f'  "{kw}": {txt.count(kw)}回')
    # 日付らしき並び
    dates = re.findall(r'\d{4}[/年]\s?\d{1,2}[/月]\s?\d{1,2}[日)]?\s*\([^)]{1,3}\)?\s*\d{1,2}:\d{2}', txt)
    print('  日時パターン:', dates[:6])
    print('  --- 本文 800字 ---')
    print('  ' + txt[:800])
