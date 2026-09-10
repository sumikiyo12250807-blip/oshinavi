# -*- coding: utf-8 -*-
"""セットリスト（曲順）を機械で取れる情報源があるか当たる。

ユーザー提案（2026-09-10）＝「深掘りとかは曲順を載せるのもいいかも」。
🚨他所がまとめた一覧をそのまま写すのは、その人の仕事に乗ることになる。
   一次情報に近いところ／APIがあるところを探す。
"""
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

CANDS = [
    ('setlist.fm トップ', 'https://www.setlist.fm/'),
    ('setlist.fm API 案内', 'https://api.setlist.fm/docs/1.0/index.html'),
    ('LiveFans セットリスト', 'https://www.livefans.jp/'),
    ('セトリレポのブログ', 'https://jununderthesamesky.com/live-report-2026/'),
]

for name, u in CANDS:
    try:
        req = urllib.request.Request(u, headers=UA)
        r = urllib.request.urlopen(req, timeout=25)
        body = r.read().decode('utf-8', 'replace')
    except Exception as ex:
        print('%-24s ❌ %r' % (name, ex))
        continue
    txt = re.sub(r'<script.*?</script>', ' ', body, flags=re.S)
    txt = re.sub(r'<[^>]+>', ' ', txt)
    txt = re.sub(r'\s+', ' ', txt)
    print('%-24s ✅ status=%s len=%-7d' % (name, r.status, len(body)))
    print('     %s' % txt[:200])
