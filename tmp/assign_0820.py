# -*- coding: utf-8 -*-
"""2026-08-20 新着プール37件の振り分け。
ジャンルは harvest 時に記憶したぴあカテゴリ（_genre）をそのまま採用＝こちらで再分類しない
（project_vendor_genre_autoassign）。_genre が空・不明のものは振り分けずプールに残す。
検証＝独立再照合（指摘2件・うち1件は本物で修正済）＋別エージェント2本のゼロ導出で全件一致。
"""
import json, re, sys, shutil, io
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

done, hold, rows = 0, [], []
for e in EVENTS:
    if e.get('genre') != 'new':
        continue
    g = (e.get('_genre') or '').strip()
    if not g or g in ('new', 'その他', 'etc'):
        hold.append((e['id'], e.get('artist'), e.get('_piaSub')))
        continue
    e['genre'] = g
    done += 1
    rows.append((e['id'], e.get('artist'), g, (e.get('links') or {}).get('pia') or ''))

if done:
    shutil.copyfile('index.html', 'index.html.bak_0820_assign')
    open('index.html', 'w', encoding='utf-8').write(
        h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])

out = ["| id | 公演名 | ジャンル | 確認用URL |", "|---|---|---|---|"]
for i, a, g, u in rows:
    out.append("| %s | %s | %s | %s |" % (i, a, g, u))
io.open('tmp/assigned_rows_0820.md', 'w', encoding='utf-8').write("\n".join(out))

print('=== 振り分け %d件 / 保留 %d件 ===' % (done, len(hold)))
for i, a, s in hold:
    print('  保留 id%s %s (_piaSub=%s)' % (i, a, s))
