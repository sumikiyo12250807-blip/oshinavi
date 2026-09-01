# -*- coding: utf-8 -*-
"""削除した7件の記録を logs/removed_2026-09-02.md に残す。
URLは削除前バックアップから機械抽出する（手で書かない＝feedback_no_fabricated_output）。"""
import re, json, sys, os
sys.stdout.reconfigure(encoding='utf-8')
IDS = [1300, 1872, 3440, 3933, 4014, 4371, 5327]
h = open('index.html.bak_0902_del7', encoding='utf-8').read()
EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
by = {e['id']: e for e in EV}
lines = ['# 削除ログ 2026-09-02（朝の便）', '',
         '公演終了済み7件。`check_expired.py` が出した候補を、別エージェントに',
         '「削除は誤りという前提で」独立再導出させて全件裏取り。5327 だけ',
         'アーカイブ枠の疑いが残ったので `pia_tickets.py b2670075 --all` で実ページを確認し、',
         '3券種とも受付終了・アーカイブ枠なしを確認してから消した。', '',
         '| id | 公演名 | 会場 | 公演日 | 確認用URL |', '|---|---|---|---|---|']
for i in IDS:
    e = by.get(i)
    if not e:
        lines.append(f'| {i} | (バックアップに見つからない) | | | |')
        continue
    url = ((e.get('links') or {}).get('pia') or '') or (e.get('url') or '')
    if not url:
        for t in (e.get('tickets') or []):
            if t.get('url'):
                url = t['url']
                break
    lines.append(f"| {i} | {e.get('artist','')} | {e.get('venue','')} | {e.get('date','')} | {url} |")
lines += ['', '## 各枠の締切（削除前の実データ）', '']
for i in IDS:
    e = by.get(i)
    if not e:
        continue
    lines.append(f"- **id{i} {e.get('artist','')}**（公演 {e.get('date','')}）")
    for t in (e.get('tickets') or []):
        lines.append(f"    - {t.get('type','')} … 締切 {t.get('date','')}"
                     f"{' / soldout' if t.get('soldout') else ''}")
os.makedirs('logs', exist_ok=True)
open('logs/removed_2026-09-02.md', 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
print('wrote logs/removed_2026-09-02.md  lines=%d' % len(lines))
