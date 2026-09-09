# -*- coding: utf-8 -*-
"""素材で48字に切られた公演名を洗い出し、投稿の本文にその名前が正しく入っているか照らす。"""
import io, re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

DAYS = {"2026-09-10", "2026-09-11", "2026-09-12"}
h = io.open('index.html', encoding='utf-8', newline='').read()
EV = json.loads(re.search(r'const EVENTS = (\[.*?\]);\r?\n', h, re.S).group(1))

long_names = set()
for e in EV:
    if e.get('genre') == 'new':
        continue
    for t in e.get('tickets') or []:
        if t.get('startDate') in DAYS and not t.get('soldout'):
            n = e.get('name') or ''
            if len(n) > 48:
                long_names.add(n)

posts = io.open('tmp/x_posts_0910.md', encoding='utf-8').read()
print('48字を超える公演名 %d件' % len(long_names))
for n in sorted(long_names):
    ok = n in posts
    cut = n[:48]
    incut = cut in posts
    print('  %s\n    全名が本文にある: %s / 切れた形(48字)が本文にある: %s' % (n, ok, incut))
