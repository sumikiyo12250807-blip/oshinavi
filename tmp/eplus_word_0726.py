# -*- coding: utf-8 -*-
"""3075/3090 の詳細ページから /sf/word/ リンクを抽出する"""
import sys, io, re
sys.path.insert(0, 'tools')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from eplus_harvest import fetch

TARGETS = [
    ('3075 amonpeas', 'https://eplus.jp/sf/detail/3830670001-P0030011P021001'),
    ('3090 Lavt', 'https://eplus.jp/sf/detail/4247640001-P0030009P021001'),
]

for label, url in TARGETS:
    print('=' * 60)
    print(label)
    html = fetch(url)
    if not html:
        print('  FETCH FAIL')
        continue
    seen = []
    for m in re.finditer(r'href="(/sf/word/[^"]+)"[^>]*>(.*?)</a>', html, re.S):
        href, txt = m.group(1), re.sub(r'<[^>]+>', '', m.group(2)).strip()
        if (href, txt) not in seen:
            seen.append((href, txt))
    for href, txt in seen:
        print('  https://eplus.jp' + href, '|', txt[:60])
    if not seen:
        # フォールバック: word を含む全URL
        for h in sorted(set(re.findall(r'/sf/word/[0-9A-Za-z_\-]+', html))):
            print('  (raw) https://eplus.jp' + h)
