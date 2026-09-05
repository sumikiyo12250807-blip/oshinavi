# -*- coding: utf-8 -*-
"""ぴあ公演ページから会場・公演日だけ機械で抜く（照合用）。"""
import re, sys, io, urllib.request, html as H

url = sys.argv[1]
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
h = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')
txt = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', h, flags=re.S)
txt = H.unescape(re.sub(r'<[^>]+>', ' ', txt))
txt = re.sub(r'[ \t　]+', ' ', txt)
lines = [l.strip() for l in txt.splitlines() if l.strip()]
out = io.open(sys.argv[2], 'w', encoding='utf-8')
out.write(url + '\n\n')
for l in lines[:200]:
    out.write(l + '\n')
out.close()
print('OK lines=%d' % len(lines))
