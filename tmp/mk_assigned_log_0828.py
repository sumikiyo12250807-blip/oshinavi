# -*- coding: utf-8 -*-
"""今朝振り分けた分だけを logs/assigned_2026-08-28.md に残す。
対象＝HEAD時点で genre=="new" だったエントリ（git の原本と突合して確定する）。"""
import io, re, json, sys, collections, subprocess
sys.stdout.reconfigure(encoding='utf-8')

def load(txt):
    return json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', txt, re.S).group(2))

old = load(subprocess.run(['git', 'show', 'HEAD:index.html'], capture_output=True).stdout.decode('utf-8'))
new = load(io.open('index.html', encoding='utf-8', newline='').read())
was_new = {e['id'] for e in old if e.get('genre') == 'new'}
tgt = sorted([e for e in new if e['id'] in was_new], key=lambda e: e['id'])
assert len(tgt) == len(was_new), '件数が合わない %d/%d' % (len(tgt), len(was_new))
by = collections.Counter(e.get('genre') for e in tgt)

o = io.open('logs/assigned_2026-08-28.md', 'w', encoding='utf-8')
o.write('# 2026-08-28 朝 新着の振り分け（%d件・id5332-5594）\n\n' % len(tgt))
o.write('ぴあのサブカテゴリを機械で写した下書き `_genre` をそのまま適用。\n')
o.write('別エージェントがゼロから再導出して突合＝**%d件中 不一致0・_piaSub空0・未知サブ0**。\n\n' % len(tgt))
o.write('内訳: ' + ' / '.join('%s %d' % (k, v) for k, v in by.most_common()) + '\n\n')
o.write('🇰🇷 1件だけ機械の値から動かした＝**id5519 キム・チャンワンバンド**（ぴあ「音楽/海外ROCK・POPS」→ `kpop`）。\n')
o.write('　韓国のバンド「산울림(サンウルリム)」のリーダーのバンドで、ぴあにK-POP区分が無いための読み替え。\n\n')
o.write('| id | ジャンル | 公演名 | 公演日 | 確認用URL |\n|---|---|---|---|---|\n')
for e in tgt:
    L = e.get('links') or {}
    u = L.get('pia') or L.get('eplus') or L.get('rakuten') or L.get('ltike') or ''
    g = e.get('genre')
    ex = e.get('extraGenres') or []
    if ex:
        g = g + '+' + '+'.join(ex)
    o.write('| %s | %s | %s | %s | %s |\n' % (
        e['id'], g, (e.get('name') or '').replace('|', '｜'), e.get('date'), u))
o.close()
print('振り分けた件数', len(tgt))
print('内訳', dict(by))
