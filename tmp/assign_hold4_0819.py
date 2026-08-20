# -*- coding: utf-8 -*-
"""相談待ちだった4件の振り分け（2026-08-19・ユーザーが「あたしの案でいい」と明示OK）。

 4377 BE WONDERFUL!!            → jpop   （ぴあカテゴリ 音楽/J-POP・ROCK のまま。買えるのが駐車券2枠だけでも載せる）
 4400 MASTERPIECE 2026          → jpop   （ぴあにカテゴリが無い bundle。中身を裏取り＝岐阜市文化センターで
                                          11/28-29に26組が出るロックのイベント。屋内なので fes にしない＝[[feedback_fes_definition]]）
 4417 LEE SANG JUN SHOW 45      → kpop
 4418 Osaka GLOW                → kids
"""
import json, re, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

PLAN = {4377: 'jpop', 4400: 'jpop', 4417: 'kpop', 4418: 'kids'}

h = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

rows = []
for e in EVENTS:
    g = PLAN.get(e['id'])
    if not g or e.get('genre') != 'new':
        continue
    e['genre'] = g
    for k in ('_genre', '_extraGenres', '_piaSub'):
        e.pop(k, None)
    rows.append((e['id'], e['name'], g, (e.get('links') or {}).get('pia', '')))

left = [e['id'] for e in EVENTS if e.get('genre') == 'new']
print('振り分け %d件 / 新着に残る %d件' % (len(rows), len(left)))

body = h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():]
mo = re.search(r'(const NEW_ORDER\s*=\s*)(\[[^\]]*\])', body)
order = [i for i in json.loads(mo.group(2)) if i in set(left)]
body = body[:mo.start()] + mo.group(1) + json.dumps(order) + body[mo.end():]

shutil.copyfile('index.html', 'index.html.bak_0819_hold4')
open('index.html', 'w', encoding='utf-8', newline='').write(body)

with open('logs/assigned_2026-08-19.md', 'a', encoding='utf-8', newline='\n') as f:
    f.write('\n## 追記：相談待ちだった4件を振り分け（ユーザーが「あたしの案でいい」とOK）\n\n')
    f.write('| id | 公演名 | ジャンル | 決め手 | 確認用URL |\n|---|---|---|---|---|\n')
    why = {
        4377: '買えるのが駐車券2枠だけでも載せる（ぴあカテゴリ 音楽/J-POP・ROCK のまま）',
        4400: 'ぴあにカテゴリ無し。中身は岐阜市文化センターで11/28-29に26組が出るロックのイベント。**屋内なので fes にしない**',
        4417: '韓国のアーティストのワールドツアー公演',
        4418: '暗闇で光るダンスのパフォーマンス＆体験',
    }
    for i, name, g, url in rows:
        f.write('| %d | %s | %s | %s | %s |\n' % (i, name.replace('|', '/'), g, why[i], url))
    f.write('\n4400 の裏取り＝公式 http://masterpiece-gifu.com/ ／ ジェイルハウス https://www.jailhouse.jp/masterpiece2026/ '
            '（DAY1 13組・DAY2 13組）\n')

for i, name, g, url in rows:
    print('  %d %s → %s' % (i, name[:40], g))
print('NEW_ORDER %d件' % len(order))
