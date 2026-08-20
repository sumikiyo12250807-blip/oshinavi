# -*- coding: utf-8 -*-
"""新着プールの振り分け（2026-08-19）。
下書き `_genre` / `_extraGenres`（ぴあカテゴリ由来）を正式な genre / extraGenres へ移す。
自分の知識で再分類はしない＝[[project_vendor_genre_autoassign]]。
相談待ちの4件（4377 / 4400 / 4417 / 4418）は new のまま残す。
NEW_ORDER も残す4件だけに揃える（[[feedback_new_order_array]]）。
検証＝独立再照合（指摘0）＋別エージェント2本のゼロ導出（26件とも枠数・千秋楽・県・ジャンル一致）。
"""
import json, re, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

HOLD = {4377, 4400, 4417, 4418}

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

rows = []
for e in EVENTS:
    if e.get('genre') != 'new' or e['id'] in HOLD:
        continue
    g = e.get('_genre')
    if not g:
        print('!! id=%d に _genre が無い。中止' % e['id'])
        sys.exit(1)
    extra = e.get('_extraGenres') or []
    e['genre'] = g
    if extra:
        e['extraGenres'] = extra
    for k in ('_genre', '_extraGenres', '_piaSub'):
        e.pop(k, None)
    rows.append((e['id'], e['name'], g, extra, (e.get('links') or {}).get('pia', '')))

left = [e['id'] for e in EVENTS if e.get('genre') == 'new']
print('振り分け %d件 / 新着に残す %d件 %s' % (len(rows), len(left), left))

body = h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():]

# NEW_ORDER を残った4件に揃える
mo = re.search(r'(const NEW_ORDER\s*=\s*)(\[[^\]]*\])', body)
if not mo:
    print('!! NEW_ORDER が見つからない。中止')
    sys.exit(1)
body = body[:mo.start()] + mo.group(1) + json.dumps(left) + body[mo.end():]

shutil.copyfile('index.html', 'index.html.bak_0819_assign')
open('index.html', 'w', encoding='utf-8').write(body)

with open('logs/assigned_2026-08-19.md', 'w', encoding='utf-8', newline='\n') as f:
    f.write('# 2026-08-19 新着の振り分け %d件\n\n' % len(rows))
    f.write('前夜（8/18 午後）に投入した50件のうち、既存エントリへ統合した25件を除く26件。\n')
    f.write('ジャンルは harvest 時に記憶したぴあカテゴリ（`_piaSub`）をそのまま適用＝こちらで再分類していない。\n\n')
    f.write('検証＝①独立再照合スクリプト（実ページから作り直して突合）で指摘0件\n')
    f.write('②別エージェント2本に、こちらの登録値を伏せてぴあ実ページからゼロ導出させ、\n')
    f.write('　**26件すべて 枠数・千秋楽・都道府県・ジャンルが一致**（不一致0）。\n\n')
    f.write('| id | 公演名 | ジャンル | 確認用URL |\n|---|---|---|---|\n')
    for i, name, g, extra, url in rows:
        lab = g + ('＋' + '＋'.join(extra) if extra else '')
        f.write('| %d | %s | %s | %s |\n' % (i, name.replace('|', '/'), lab, url))
    f.write('\n## 新着に残した4件（ユーザーが考え中）\n\n')
    f.write('| id | 公演名 | 迷っている点 |\n|---|---|---|\n')
    f.write('| 4377 | BE WONDERFUL!! | 買えるのが駐車券2枠だけ（終わった先行枠は今朝掃除した） |\n')
    f.write('| 4400 | MASTERPIECE 2026 | ぴあのカテゴリが取れずジャンル不明 |\n')
    f.write('| 4417 | 2026 LEE SANG JUN SHOW 45 | kpop か musicetc か |\n')
    f.write('| 4418 | Osaka GLOW Glow-in-the-Dark Dance | art か kids か |\n')

for i, name, g, extra, url in rows:
    print('  %d %s → %s%s' % (i, name[:34], g, '+' + '+'.join(extra) if extra else ''))
print('=== logs/assigned_2026-08-19.md に記録 ===')
