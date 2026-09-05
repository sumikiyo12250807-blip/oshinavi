# -*- coding: utf-8 -*-
import io, re, glob, sys
import html as H
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
p = glob.glob(r'C:\Users\user\oshinavi\tmp\vfy_html_0905\*4590340001*')[0]
h = io.open(p, encoding='utf-8').read()
t = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', H.unescape(h)))
i = t.find('出演')
out = []
while i != -1 and len(out) < 6:
    out.append(t[max(0, i - 120):i + 400])
    i = t.find('出演', i + 1)
io.open(r'C:\Users\user\oshinavi\tmp\vfy_meme2.txt', 'w', encoding='utf-8').write('\n\n----\n'.join(out))
print('ok')
