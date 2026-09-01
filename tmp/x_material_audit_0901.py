# -*- coding: utf-8 -*-
"""X素材（9/2・9/3・9/4の発売開始）の取りこぼし監査。

x_material_0901.py は2つの条件で枠を捨てている。その落とし分を数える。
  ① 券種名が「M/D HH:MM発売」の形でないと拾わない
  ② genre:"new"（新着プール）で NEWMAP にも _genre にも当たらないと束が決まらず捨てる
さらにヒール適用後の index.html で件数を再導出して、素材ファイルと突き合わせる。
出力は tmp/x_material_audit_0901.txt（コンソールに日本語を出さない）。
"""
import collections
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

DAYS = {'2026-09-02': '9/2(水)', '2026-09-03': '9/3(木)', '2026-09-04': '9/4(金)'}
BUCKET = [
    ('音楽', {'jpop', 'rock', 'enka', 'idol', 'kpop', 'yougaku', 'anime', 'musicetc', 'chanson'}),
    ('クラシック', {'classic', 'dento', 'jazz'}),
    ('舞台・映画', {'engeki', 'musical', '2.5ji', 'aisatsu', 'art'}),
    ('お笑い', {'owarai'}),
    ('スポーツ', {'sports'}),
]
NEWMAP = {
    5996: '音楽', 6009: '音楽', 6010: '音楽', 6014: '音楽', 6040: '音楽', 6044: '音楽',
    6045: '音楽', 6053: '音楽', 6063: '音楽', 6183: '音楽', 6086: '音楽',
    6119: 'お笑い', 6127: 'お笑い', 6134: 'お笑い',
    6136: '舞台・映画', 6137: '舞台・映画', 6145: '舞台・映画', 6146: '舞台・映画',
    6139: 'スポーツ', 6140: 'スポーツ', 6142: 'スポーツ', 6143: 'スポーツ',
}
src = io.open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'const EVENTS = (\[.*?\]);\n', src, re.S).group(1))
G2B = {g: b for b, gs in BUCKET for g in gs}

kept = collections.defaultdict(lambda: collections.defaultdict(set))
drop_regex = []
drop_bucket = []
for e in EVENTS:
    g = e.get('genre') or ''
    b = NEWMAP.get(e['id']) if g == 'new' else G2B.get(g)
    if g == 'new' and not b:
        b = G2B.get(e.get('_genre') or '')
    for t in e.get('tickets', []):
        if t.get('soldout'):
            continue
        sd = t.get('startDate')
        if sd not in DAYS:
            continue
        has_regex = bool(re.search(r'(\d{1,2})/(\d{1,2})\s+(\d{1,2}:\d{2})発売', t.get('type', '')))
        if not b:
            drop_bucket.append((sd, e['id'], e.get('artist', ''), g, e.get('_genre'), t.get('type', '')))
            continue
        if not has_regex:
            drop_regex.append((sd, e['id'], e.get('artist', ''), b, t.get('type', '')))
            continue
        kept[sd][b].add(re.sub(r'\s+', '', e.get('artist', '')))

out = []
out.append('=== ヒール適用後の index.html で数え直した「発売開始」件数（1エントリ1件に畳んだ数）===')
for sd in sorted(DAYS):
    out.append('--- %s ---' % DAYS[sd])
    for b, _ in BUCKET:
        out.append('    %-12s %d組' % (b, len(kept[sd].get(b, ()))))
out.append('')
out.append('=== ①券種名が「M/D HH:MM発売」の形でないため素材から落ちた枠 = %d ===' % len(drop_regex))
for sd, i, a, b, ty in sorted(drop_regex):
    out.append('  %s [%s] id%-6s %-34s | %s' % (DAYS[sd], b, i, a[:34], ty))
out.append('')
out.append('=== ②束が決まらず落ちたエントリの枠 = %d ===' % len(drop_bucket))
for sd, i, a, g, _g, ty in sorted(drop_bucket):
    out.append('  %s id%-6s %-34s genre=%s _genre=%s | %s' % (DAYS[sd], i, a[:34], g, _g, ty))

io.open('tmp/x_material_audit_0901.txt', 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
print('WROTE tmp/x_material_audit_0901.txt  drop_regex=%d drop_bucket=%d' % (len(drop_regex), len(drop_bucket)))
