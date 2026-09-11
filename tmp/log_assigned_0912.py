# -*- coding: utf-8 -*-
"""振り分ける前の新着プールから、振り分け予定の分を logs/assigned_2026-09-12.md に書き出す（読むだけ・logsだけ書く）。
振り分けで新着タブは空になるので、ここが「後から見る場所」になる（memory feedback_new_pool_ok_before_assign）。
使い方: python tmp/log_assigned_0912.py <除外id,...>
"""
import collections
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
skip = {int(x) for x in sys.argv[1].split(',') if x.strip()} if len(sys.argv) > 1 else set()
src = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
pool = [e for e in ev if e.get('genre') == 'new' and e['id'] not in skip]
held = [e for e in ev if e.get('genre') == 'new' and e['id'] in skip]
by_g = collections.defaultdict(list)
for e in pool:
    by_g[e.get('_genre') or '(下書き無し)'].append(e)

with io.open('logs/assigned_2026-09-12.md', 'w', encoding='utf-8') as f:
    f.write('# 2026-09-12 に新着タブから振り分けたもの（%d件）\n\n' % len(pool))
    f.write('対象＝9/11 に入れたぴあ由来の新着（id7840〜8157）。\n')
    f.write('別エージェント4本がぴあの実ページからゼロで再導出（232件とも読めた・読めなかったのは7946の1件）。\n')
    f.write('ジャンルは、下書き（ぴあの区分を対応表に通したもの）232件とも対応表どおり、\n')
    f.write('エージェントが実ページから読んだぴあの区分とも食い違いなし。\n')
    f.write('再チェックで直したもの＝7882パレイドリア・8145 WHITE JAM（会期）／8149桂文珍（一般発売10/16を追加）／\n')
    f.write('7933天皇杯（6会場・全国）／7959 THAI ON FES（今日の当日券）／7975・8009（これからの公演を会期に）。\n\n')
    f.write('新着タブに残したもの＝%s\n' % '、'.join('id%s %s' % (e['id'], (e.get('name') or '')[:24]) for e in held))
    f.write('（7558/7741/7744＝前からの保留／7946＝ぴあのページが消えて後継が見つからない／8158〜8160＝今朝入れた分・明日の再チェック待ち）\n')
    for g in sorted(by_g):
        f.write('\n## %s\n\n' % g)
        for e in sorted(by_g[g], key=lambda x: x['id']):
            L = e.get('links') or {}
            url = L.get('pia') or L.get('eplus') or L.get('rakuten') or L.get('lawson') or ''
            f.write('- id=%s %s（%s）\n' % (e['id'], e.get('name') or '', e.get('date') or ''))
            if url:
                f.write('  - %s\n' % url)
print('振り分け予定 %d件 → logs/assigned_2026-09-12.md ／ 残す %d件' % (len(pool), len(held)))
print('ジャンル内訳: %s' % {g: len(v) for g, v in sorted(by_g.items())})
