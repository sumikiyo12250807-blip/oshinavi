# -*- coding: utf-8 -*-
"""ジャンル追加の検算：index.html と build_ai_page.py の GENRE_LABEL が一致しているか、
ボタン・グループ・データが揃っているか。写経でなく実物から取る。"""
import re, sys, json
sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import build_ai_page as B

h = open('index.html', encoding='utf-8', newline='').read()
lab = re.search(r'const GENRE_LABEL = \{(.*?)\};', h, re.S).group(1)
keys_html = set(re.findall(r'(?:^|[\s,{])"?([A-Za-z0-9.]+)"?\s*:', lab))
btns = set(re.findall(r'data-genre="([^"]+)"', h))
grp = re.search(r'const GENRE_GROUPS = \{(.*?)\};', h, re.S).group(1)
grp_members = set(re.findall(r'"([a-z0-9.]+)"', grp))

for g in ('fanevent', 'kaigai', 'gourmet'):
    print('%-9s GENRE_LABEL=%-5s ボタン=%-5s グループ所属=%-5s ai側LABEL=%s' % (
        g, g in keys_html, g in btns, g in grp_members, B.GENRE_LABEL.get(g)))

diff = keys_html - set(B.GENRE_LABEL) - {'new'}
print('index側にあって ai側に無いジャンル:', sorted(diff))

EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
for e in EV:
    if e.get('id') in (4258, 4259, 4260):
        print('id%s genre=%-9s extra=%-14s 下書き残り=%s  %s' % (
            e['id'], e.get('genre'), e.get('extraGenres'),
            [k for k in ('_genre', '_extraGenres', '_piaSub') if k in e],
            (e.get('name') or '')[:36]))
print('genre:new の残り', sum(1 for e in EV if e.get('genre') == 'new'), '件')
