# -*- coding: utf-8 -*-
"""振り分け結果を logs/assigned_YYYY-MM-DD.md に残す（新着タブが空になる代わりの「見る場所」）。
[[feedback_new_pool_ok_before_assign]] の C＝後から見られるリンクを残す。"""
import json, io, sys, collections
sys.stdout.reconfigure(encoding='utf-8')

dec = json.load(io.open('tmp/assign_decided_0825.json', encoding='utf-8'))
theirs = json.load(io.open('tmp/genre_out_0825.json', encoding='utf-8'))
plan = json.load(io.open('tmp/assign_plan_0825.json', encoding='utf-8'))
mine = {str(r['id']): r for r in plan['auto']}

out = []
out.append('# 振り分けログ 2026-08-25（朝の便）')
out.append('')
out.append('新着プール **87件** のうち **%d件** を正式ジャンルへ振り分けた。' % len(dec['apply']))
out.append('判定は「ぴあが付けているサブジャンルをそのまま写す」原則（project_vendor_genre_autoassign）。')
out.append('別エージェントに**下書きを見せずゼロから判定**させ、**一致したものだけ**を適用した。')
out.append('割れた件・エージェントが自信なしと言った件は **振り分けずプールに残した**（下の表）。')
out.append('')
c = collections.Counter(r['genre'] for r in dec['apply'])
out.append('内訳: ' + ' / '.join('%s %d' % kv for kv in c.most_common()))
out.append('')
out.append('| id | 公演名 | ジャンル | ぴあの区分 | 確認用URL |')
out.append('|---|---|---|---|---|')
for r in sorted(dec['apply'], key=lambda x: x['id']):
    out.append('| %d | %s | %s | %s | %s |' % (
        r['id'], r['name'], r['genre'], r['sub'], r['url'] or ''))

out.append('')
out.append('## ⚠️振り分けずプールに残した %d件（相談待ち）' % len(dec['hold']))
out.append('')
out.append('| id | 公演名 | ぴあの区分 | あたしの下書き | 検証エージェント | 迷いどころ |')
out.append('|---|---|---|---|---|---|')
for k in dec['hold']:
    m = mine[k]
    t = theirs.get(k, {})
    note = (t.get('note') or '').replace('\n', ' ')
    out.append('| %s | %s | %s | %s | %s | %s |' % (
        k, m['name'], m['sub'], m['genre'], t.get('genre', '?'), note))
out.append('')
out.append('確認用URL:')
for k in dec['hold']:
    out.append('- %s %s' % (mine[k]['name'], mine[k]['url'] or ''))

io.open('logs/assigned_2026-08-25.md', 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
print('logs/assigned_2026-08-25.md を書いた（適用%d件 / 保留%d件）' % (len(dec['apply']), len(dec['hold'])))
