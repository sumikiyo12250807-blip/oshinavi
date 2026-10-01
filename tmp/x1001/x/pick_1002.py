# -*- coding: utf-8 -*-
"""夜のX投稿の素材＝**明日10/2(金)に発売が始まる枠**を機械で抜く（tmp/x0930/x/pick_1001.py の日付違い）。
出力: tmp/x1001/x/pick_1002.md（ジャンル別）／pick_1002.json
"""
import io, json, re, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')
TOMORROW = '2026-10-02'
h = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[)', h)
EVENTS, _ = json.JSONDecoder().raw_decode(h, m.start(1))
by_genre = defaultdict(list)
rows = []
for e in EVENTS:
    if e.get('genre') == 'new':
        continue
    for t in (e.get('tickets') or []):
        if t.get('startDate') != TOMORROW:
            continue
        tail = re.sub(r'^.*[）)]', '', t.get('type') or '')
        tm = re.search(r'(\d{1,2}:\d{2})\s*(?:発売|受付)', tail)
        r = {'id': e['id'], 'artist': e.get('artist'), 'name': e.get('name'), 'genre': e.get('genre'),
             'extra': e.get('extraGenres') or [], 'pref': e.get('prefecture'), 'date': e.get('date'),
             'dateLabel': e.get('dateLabel'), 'venue': e.get('venue'), 'type': t.get('type'),
             'time': tm.group(1) if tm else '', 'url': t.get('url')}
        rows.append(r)
        by_genre[e.get('genre')].append(r)
        break
io.open('tmp/x1001/x/pick_1002.json', 'w', encoding='utf-8').write(json.dumps(rows, ensure_ascii=False, indent=1))
with io.open('tmp/x1001/x/pick_1002.md', 'w', encoding='utf-8') as f:
    f.write('# 10/2(金)に発売が始まる枠（ジャンル別・夜のX投稿の素材）\n')
    for g in sorted(by_genre, key=lambda k: -len(by_genre[k])):
        f.write('\n## %s（%d）\n\n' % (g, len(by_genre[g])))
        for r in sorted(by_genre[g], key=lambda r: (r['time'] or '99:99', r['artist'] or '')):
            f.write('- %s %s（%s %s）id%s\n  %s\n' % (r['time'] or '時刻なし', r['artist'], r['pref'] or '',
                                                     (r['dateLabel'] or '')[:34], r['id'], r['type']))
print('明日発売のエントリ %d件 / ジャンル %d' % (len(rows), len(by_genre)))
for g in sorted(by_genre, key=lambda k: -len(by_genre[k])):
    print('  %-10s %d' % (g, len(by_genre[g])))
