# -*- coding: utf-8 -*-
"""夜のX投稿の素材＝**明日9/21(月・祝)に発売が始まる枠**を機械で抜く（2026-09-20 昼に先出し）。

X_SCRIPT の本数の決め方＝①トレンド枠0〜1本 ②主役枠（Xフォロワー上位3組）③残りはジャンル別まとめ。
ここは③のための一覧作り。**件数は書かない**（網羅していないので嘘になる＝[[feedback_x_no_counts_oshi_first]]）。
出力: tmp/x0920/pick_0921.md（ジャンル別）／tmp/x0920/pick_0921.json
"""
import io, json, re, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')
TOMORROW = '2026-09-21'

h = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

by_genre = defaultdict(list)
rows = []
for e in EVENTS:
    if e.get('genre') == 'new':
        continue
    for t in (e.get('tickets') or []):
        if t.get('startDate') != TOMORROW:
            continue
        tm = re.search(r'(\d{1,2}:\d{2})', t.get('type') or '')
        r = {'id': e['id'], 'artist': e.get('artist'), 'genre': e.get('genre'),
             'pref': e.get('prefecture'), 'date': e.get('date'),
             'dateLabel': e.get('dateLabel'), 'type': t.get('type'),
             'time': tm.group(1) if tm else '', 'url': t.get('url')}
        rows.append(r)
        by_genre[e.get('genre')].append(r)
        break                      # 1エントリ1行でよい

io.open('tmp/x0920/pick_0921.json', 'w', encoding='utf-8').write(
    json.dumps(rows, ensure_ascii=False, indent=1))
with io.open('tmp/x0920/pick_0921.md', 'w', encoding='utf-8') as f:
    f.write('# 9/21(月・祝)に発売が始まる枠（ジャンル別・夜のX投稿の素材）\n')
    for g in sorted(by_genre, key=lambda k: -len(by_genre[k])):
        f.write('\n## %s\n\n' % g)
        for r in sorted(by_genre[g], key=lambda r: (r['time'] or '99:99', r['artist'] or '')):
            f.write('- %s %s（%s %s）id%s\n  %s\n'
                    % (r['time'] or '時刻なし', r['artist'], r['pref'] or '',
                       (r['dateLabel'] or '')[:34], r['id'], r['type']))
print('明日発売のエントリ %d件 / ジャンル %d' % (len(rows), len(by_genre)))
for g in sorted(by_genre, key=lambda k: -len(by_genre[k])):
    print('  %-10s %d' % (g, len(by_genre[g])))
