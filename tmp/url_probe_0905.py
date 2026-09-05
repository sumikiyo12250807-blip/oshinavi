# -*- coding: utf-8 -*-
"""問題のURLが本当に死んでいるのか、レート制限なのかを切り分ける（間を空けて3回）。"""
import urllib.request, time, io, re

URLS = [
    'https://eplus.jp/sf/detail/4589180001-P0030001P021001',
    'https://eplus.jp/sf/detail/4589180001',
    'https://eplus.jp/sf/detail/4589140001-P0030001P021001',  # 比較用（同ツアーの通っている枠）
]
out = io.open('tmp/url_probe_0905.txt', 'w', encoding='utf-8')
for u in URLS:
    for i in range(3):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30)
            body = r.read().decode('utf-8', 'replace')
            ld = re.findall(r'<script type="application/ld\+json">(.*?)</script>', body, re.S)
            nm = re.search(r'"name"\s*:\s*"([^"]+)"', ld[0]) if ld else None
            st = re.search(r'"startDate"\s*:\s*"([^"]+)"', ld[0]) if ld else None
            out.write('%s\n  try%d HTTP=%d len=%d LD=%d name=%s start=%s\n'
                      % (u, i + 1, r.status, len(body), len(ld),
                         nm.group(1) if nm else '-', st.group(1) if st else '-'))
            break
        except Exception as e:
            out.write('%s\n  try%d ERROR %s\n' % (u, i + 1, e))
            time.sleep(8)
out.close()
print('OK')
