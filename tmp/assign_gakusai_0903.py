# -*- coding: utf-8 -*-
"""9/2から保留していたe+の学園祭7件を genre:"gakusai" に振り分ける（ユーザー指示 2026-09-03）。

🚨 assign_genres.py は genre:"new" を全部さらうので使わない。
   今朝投入した新規64件は「翌朝チェックしてから振り分ける」約束なので、絶対に巻き込まない。
   （memory: feedback_new_pool_ok_before_assign / feedback_new_list_order_lock）
NEW_ORDER からも同じ7件だけを抜く（並び順配列と genre:"new" の件数を必ず一致させる）。
CRLF保持は assign_genres.py と同じ方式。
"""
import re, json, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TARGET = [6012, 6211, 6212, 6216, 6224, 6227, 6228]
PATH = 'index.html'

src = open(PATH, encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in src else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))

hit = 0
for e in events:
    if e['id'] in TARGET:
        assert e.get('genre') == 'new', 'id%d が genre:"new" でない' % e['id']
        assert '大学' in (e.get('venue') or '') or '大学' in (e.get('name') or ''), \
            'id%d は大学の会場に見えない' % e['id']
        e['genre'] = 'gakusai'
        for f in ('_genre', '_extraGenres', '_piaSub', '_srcgenre'):
            e.pop(f, None)
        hit += 1
        print('  id%d %s' % (e['id'], (e.get('name') or '')[:50]))

assert hit == len(TARGET), '対象が %d件しか無い' % hit

m2 = re.search(r'(const NEW_ORDER = )(\[[^\]]*\])(;)', src)
order = [i for i in json.loads(m2.group(2)) if i not in TARGET]

remain = [e['id'] for e in events if e.get('genre') == 'new']
assert sorted(remain) == sorted(order), 'NEW_ORDER と genre:"new" が食い違う'

open('index.html.bak_0903_gakusai', 'w', encoding='utf-8', newline='').write(src)
dumped = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl)
out = src[:m.start()] + m.group(1) + dumped + m.group(3) + src[m.end():]
out = out[:m2.start()] + m2.group(1) + json.dumps(order) + m2.group(3) + out[m2.end():]
open(PATH, 'w', encoding='utf-8', newline='').write(out)
print('=== 学園祭へ %d件 / 新着プール残り %d件 ===' % (hit, len(remain)))
