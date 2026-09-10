# -*- coding: utf-8 -*-
"""次号「今週のピックアップ」（9/13(日)朝 公開・対象 9/14(月)〜9/20(日)）の素材を全部並べる。

🚨**選んでから確かめるのをやめて、選ぶ前に並べる**（[[feedback_article_recheck_after_rewrite]]）。
2026-09-06 は窓の発売356件に対し記事17組で、沢田研二・モーニング娘。'26 などが漏れた。

出すもの:
  ①この窓で「発売が始まる」枠を持つエントリを全部
  ②アーティスト単位で「枠数の多い順」「会場数の多い順」＝今週まとめて出るのは誰か
  ③大きめの会場（アリーナ・ドーム・大ホール等）の印
"""
import collections
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
FROM, TO = '2026-09-14', '2026-09-20'

BIG = re.compile(r'ドーム|アリーナ|武道館|スタジアム|国際フォーラム|フェスティバルホール|'
                 r'サンプラザ|Zepp|ぴあアリーナ|横浜アリーナ|さいたまスーパーアリーナ|'
                 r'大ホール|オペラパレス|NHKホール|オーチャード|中野サンプラザ|'
                 r'東京ガーデンシアター|LINE CUBE|舞浜|城ホール|グランキューブ|'
                 r'フォレストホール|ロームシアター|愛知県芸術劇場|オリックス劇場|'
                 r'コンサートホール|文化会館|市民会館|芸術劇場')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
events = json.loads(m.group(2))

rows = []
for e in events:
    if e.get('genre') == 'new':
        continue                     # 新着プールは記事に出さない（振り分け前）
    hits = []
    for t in e.get('tickets') or []:
        sd = t.get('startDate')
        if sd and FROM <= sd <= TO:
            hits.append(t)
    if hits:
        rows.append((e, hits))

print('=== 9/14(月)〜9/20(日) に発売が始まるエントリ: %d件 / 枠 %d ==='
      % (len(rows), sum(len(h2) for _, h2 in rows)))

# アーティスト単位（同名は畳む）
by = collections.defaultdict(lambda: {'slots': 0, 'venues': set(), 'ids': set(),
                                      'genre': '', 'dates': set(), 'big': False})
for e, hits in rows:
    k = (e.get('artist') or e.get('name') or '').strip()
    a = by[k]
    a['slots'] += len(hits)
    a['ids'].add(e['id'])
    a['genre'] = e.get('genre')
    for t in hits:
        a['dates'].add(t['startDate'])
    v = (e.get('venue') or '') + ' ' + (e.get('dateLabel') or '')
    for x in re.split(r'[／/]', re.sub(r'^全国ツアー（|）$', '', e.get('venue') or '')):
        if x.strip():
            a['venues'].add(x.strip())
    if BIG.search(v):
        a['big'] = True

order = sorted(by.items(), key=lambda kv: (-kv[1]['slots'], -len(kv[1]['venues'])))
print('\n=== アーティスト単位 %d組（枠数の多い順）===' % len(order))
for k, a in order[:60]:
    print('  %-34s 枠%-3d 会場%-2d [%s]%s  発売日 %s  id=%s'
          % (k[:34], a['slots'], len(a['venues']), a['genre'],
             ' 🏟' if a['big'] else '  ', '/'.join(sorted(a['dates']))[:34],
             ','.join(str(i) for i in sorted(a['ids']))[:20]))

with open('tmp/pickup_window_0914.txt', 'w', encoding='utf-8') as f:
    f.write('# 9/14(月)〜9/20(日) に発売が始まる分（全部）\n\n')
    f.write('エントリ %d件 / 枠 %d / アーティスト %d組\n\n'
            % (len(rows), sum(len(h2) for _, h2 in rows), len(order)))
    for k, a in order:
        f.write('- %s ／ 枠%d ／ 会場%d ／ [%s]%s ／ 発売 %s ／ id=%s\n'
                % (k, a['slots'], len(a['venues']), a['genre'],
                   ' 🏟大きめの会場' if a['big'] else '',
                   '/'.join(sorted(a['dates'])), ','.join(str(i) for i in sorted(a['ids']))))
        for v in sorted(a['venues'])[:6]:
            f.write('    %s\n' % v)
print('\n→ tmp/pickup_window_0914.txt')
