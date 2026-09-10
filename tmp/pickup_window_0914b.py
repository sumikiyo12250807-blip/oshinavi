# -*- coding: utf-8 -*-
"""日曜9/13に出す記事の素材＝9/14(月)〜9/20(日)に発売が始まる分を**全部**並べる。

🚨[[feedback_article_recheck_after_rewrite]]＝
   「選んでから確かめる」のをやめて、**選ぶ前に窓の全件を並べる**。
   2026-09-06に、356件の窓に対して記事が17組で、沢田研二・モー娘。が漏れた。

出力＝tmp/pickup_window_0914b.txt
  ①アーティスト単位（枠数の多い順＝その週にまとめて出る組が上に来る）
  ②大きめの会場に🏟印（主役を選ぶ手がかり・キャパはDBに無いので会場名で機械判定）
  ③ジャンル別の件数
"""
import collections
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

FROM, TO = '2026-09-14', '2026-09-20'

BIG = re.compile(r'アリーナ|ドーム|Zepp|ZEPP|国際フォーラム|大ホール|hitaru|ホールA|'
                 r'サンプラザ|オーチャード|オペラパレス|NHKホール|サントリーホール|'
                 r'東京芸術劇場|フェスティバルホール|オペラシティ|ミューザ|文化会館|'
                 r'市民会館|芸術劇場|スタジアム|コンサートホール|歌劇場|武道館|'
                 r'グランドホール|パシフィコ|センチュリーホール')

h = io.open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))

rows = []
for e in EVENTS:
    if e.get('genre') == 'new':
        continue                      # 新着プールは振り分け前なので記事に出さない
    slots = [t for t in (e.get('tickets') or [])
             if t.get('startDate') and FROM <= t['startDate'] <= TO and not t.get('soldout')]
    if slots:
        rows.append((e, slots))

out = io.open('tmp/pickup_window_0914b.txt', 'w', encoding='utf-8')
w = out.write

w('# %s(月)〜%s(日) に発売が始まる分（全部）\n\n' % (FROM[5:].replace('-', '/'),
                                        TO[5:].replace('-', '/')))
w('エントリ %d件 / 枠 %d / アーティスト %d組\n\n'
  % (len(rows), sum(len(s) for _, s in rows),
     len({(e.get('artist') or e.get('name')) for e, _ in rows})))
w('🚨この一覧から選ぶ。**選んでから確かめない**（[[feedback_article_recheck_after_rewrite]]）\n\n')

# ① 枠数の多い順＝その週にまとめて出る組
w('## ① 枠数の多い順（＝その週にまとめて発売になる組）\n\n')
for e, slots in sorted(rows, key=lambda x: (-len(x[1]), x[0]['id'])):
    venue = e.get('venue') or ''
    mark = ' 🏟大きめの会場' if BIG.search(venue) else ''
    days = sorted({t['startDate'] for t in slots})
    w('- %s ／ 枠%d ／ [%s]%s ／ 発売 %s ／ id=%d\n'
      % ((e.get('artist') or e.get('name') or '')[:60], len(slots),
         e.get('genre'), mark, '/'.join(days), e['id']))
    w('    %s ／ 公演 %s\n' % (venue[:80], e.get('dateLabel') or e.get('date')))

# ② 大きめの会場だけ
w('\n\n## ② 大きめの会場だけ（主役を選ぶ手がかり）\n\n')
big = [(e, s) for e, s in rows if BIG.search(e.get('venue') or '')]
w('%d件\n\n' % len(big))
for e, slots in sorted(big, key=lambda x: (-len(x[1]), x[0]['id'])):
    w('- %-46s [%s] 枠%d id=%d\n'
      % ((e.get('artist') or e.get('name') or '')[:46], e.get('genre'), len(slots), e['id']))
    w('    %s\n' % (e.get('venue') or '')[:80])

# ③ ジャンル別
w('\n\n## ③ ジャンル別の件数\n\n')
c = collections.Counter(e.get('genre') for e, _ in rows)
for g, n in c.most_common():
    w('  %-12s %d件\n' % (g, n))

out.close()
print('→ tmp/pickup_window_0914b.txt')
print('エントリ %d件 / 大きめの会場 %d件 / %dジャンル' % (len(rows), len(big), len(c)))
