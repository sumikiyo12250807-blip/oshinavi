# -*- coding: utf-8 -*-
"""6935 の出演欄を区切り込みで確認する。"""
import io, re, glob, sys
import html as H
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
p = glob.glob(r'C:\Users\user\oshinavi\tmp\vfy_html_0905\*4589250001*')[0]
h = io.open(p, encoding='utf-8').read()
out = []
i = h.find('出演')
while i != -1 and len(out) < 4:
    out.append(re.sub(r'\s+', ' ', h[max(0, i - 200):i + 1400]))
    i = h.find('出演', i + 1)
io.open(r'C:\Users\user\oshinavi\tmp\vfy_perf2_0905.txt', 'w', encoding='utf-8').write('\n\n----\n'.join(out))
print('ok')
