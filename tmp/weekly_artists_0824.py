# -*- coding: utf-8 -*-
"""「今週のピックアップ」の素材＝対象週に発売が始まる枠を**アーティスト単位**で数える。

主役は件数ではなく**アーティスト名**（2026-08-20 ユーザー指摘）。
「今週まとめて一斉に出るのは誰か」を機械で出すのが目的。

  python tmp/weekly_artists_0824.py 2026-08-24 2026-08-30
"""
import re, io, sys, json, collections, datetime

sys.stdout.reconfigure(encoding='utf-8')
FROM = sys.argv[1] if len(sys.argv) > 1 else '2026-08-24'
TO = sys.argv[2] if len(sys.argv) > 2 else '2026-08-30'

h = io.open('index.html', encoding='utf-8').read()
E = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))

rows = []
for e in E:
    hit = []
    for t in (e.get('tickets') or []):
        if t.get('soldout') or t.get('saleEnded'):
            continue
        sd = t.get('startDate') or ''
        if not (FROM <= sd <= TO):
            continue
        if not re.search(r'\d{1,2}/\d{1,2}\s*\d{1,2}:\d{2}発売', t.get('type') or ''):
            continue
        hit.append(t)
    if hit:
        rows.append((e, hit))

# アーティスト単位に束ねる
by_artist = collections.defaultdict(lambda: {'slots': [], 'events': set(), 'genre': None})
for e, hit in rows:
    a = e.get('artist') or e.get('name')
    by_artist[a]['events'].add(e['id'])
    by_artist[a]['genre'] = e.get('genre')
    for t in hit:
        by_artist[a]['slots'].append((e['id'], e.get('name'), t['type'], t.get('startDate')))

o = io.open('tmp/weekly_artists_0824.txt', 'w', encoding='utf-8')
o.write('=== %s〜%s に発売が始まる枠（アーティスト単位）===\n' % (FROM, TO))
o.write('対象アーティスト %d組 / 枠 %d / エントリ %d\n\n'
        % (len(by_artist), sum(len(v['slots']) for v in by_artist.values()), len(rows)))
for a, v in sorted(by_artist.items(), key=lambda kv: (-len(kv[1]['slots']), kv[0])):
    o.write('■ %s [%s] 枠%d / エントリ%d\n' % (a, v['genre'], len(v['slots']), len(v['events'])))
    for eid, name, ty, sd in sorted(v['slots'], key=lambda x: (x[3], x[2])):
        o.write('    id%-5s %s | %s\n' % (eid, sd, ty))
o.close()

# 日別の集計（記事の末尾に1行だけ添える用）
day = collections.Counter()
for e, hit in rows:
    for t in hit:
        day[t['startDate']] += 1
print('アーティスト %d組 / 枠 %d / エントリ %d' % (
    len(by_artist), sum(len(v['slots']) for v in by_artist.values()), len(rows)))
print('日別: ' + ' '.join('%s=%d' % (k[5:], day[k]) for k in sorted(day)))
print('→ tmp/weekly_artists_0824.txt')
