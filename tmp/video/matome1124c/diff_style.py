# -*- coding: utf-8 -*-
# 主役 1117（明るい背景で濃い字）と、写した 1118 の道具の違いを見る（kara_style・render・dj_text）
import io, difflib
V = 'C:/Users/user/oshinavi/tmp/video/'
out = []
for f in ('kara_style.py', 'dj_text.py', 'render.py'):
    a = io.open(V + 'matome1124c/' + f, encoding='utf-8').read().replace('matome1124c', 'X').splitlines()
    b = io.open(V + 'shuyaku1117/' + f, encoding='utf-8').read().replace('shuyaku1117', 'X').splitlines()
    out.append('######## ' + f)
    out += list(difflib.unified_diff(a, b, 'matome', 'shuyaku', lineterm='', n=0))[:120]
io.open(V + 'matome1124c/diff_style.txt', 'w', encoding='utf-8').write('\n'.join(out))
