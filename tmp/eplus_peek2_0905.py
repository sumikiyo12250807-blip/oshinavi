# -*- coding: utf-8 -*-
import re, sys, io, json, urllib.request, html as H
url = sys.argv[1]
h = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30).read().decode('utf-8', 'replace')
out = io.open(sys.argv[2], 'w', encoding='utf-8')
out.write(url + '\n\n')
for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
    try:
        d = json.loads(m.group(1))
    except Exception:
        continue
    out.write(json.dumps(d, ensure_ascii=False, indent=1)[:3000] + '\n\n')
t = re.search(r'<title>(.*?)</title>', h, re.S)
out.write('TITLE=' + H.unescape(t.group(1)).strip() + '\n' if t else 'TITLE=?\n')
out.close()
print('OK')
