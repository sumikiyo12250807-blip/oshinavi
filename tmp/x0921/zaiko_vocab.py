# -*- coding: utf-8 -*-
"""ZAIKOの個別データから**実データの語彙**を数える（推測で対応表を作らないため）。
・ジャンル名（event.genres と performers[].genres）
・券種名（front_text）が取れるか
・売り状態の組み合わせ（is_sale_started / is_sale_ended / is_sold_out / is_lottery / is_stream）
・締切（lottery_end_date）が入っているか
・会場の location から県が取れるか
"""
import collections, io, json, re, sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
src = sys.argv[1] if len(sys.argv) > 1 else 'tmp/zaiko_0921d.json'
d = json.load(io.open(src, encoding='utf-8'))
det = d.get('details') or {}
out = io.open('tmp/x0921/zaiko_vocab.txt', 'w', encoding='utf-8')
out.write('個別を引けた %d件 / 一覧 %d件 / 読めなかった %d件\n\n'
          % (len(det), len(d.get('list') or []), len(d.get('detail_errors') or [])))

eg, pg = collections.Counter(), collections.Counter()
state = collections.Counter()
noname, hasname = 0, 0
noend, hasend = 0, 0
loc = collections.Counter()
nticket = collections.Counter()
price_ng = 0
for u, e in det.items():
    for g in e.get('genres') or []:
        eg[g] += 1
    for p in e.get('performers') or []:
        for g in p.get('genres') or []:
            pg[g] += 1
    loc[e.get('venue_location') or '（空）'] += 1
    tks = e.get('tickets') or []
    nticket[len(tks)] += 1
    for t in tks:
        k = ('売切' if t.get('is_sold_out') else
             '終了' if t.get('is_sale_ended') else
             '受付前' if not t.get('is_sale_started') else '受付中')
        state[(k, '抽選' if t.get('is_lottery') else '先着',
               '配信' if t.get('is_stream') else '現地')] += 1
        if (t.get('name') or '').strip():
            hasname += 1
        else:
            noname += 1
        if t.get('end_date'):
            hasend += 1
        else:
            noend += 1
        if not (t.get('price') or '').strip():
            price_ng += 1

out.write('=== イベントのジャンル（event.genres）===\n')
for k, n in eg.most_common():
    out.write('  %-30s %4d件\n' % (k, n))
out.write('\n=== 出演者のジャンル（performers[].genres）===\n')
for k, n in pg.most_common(30):
    out.write('  %-30s %4d回\n' % (k, n))
out.write('\n=== 券種の状態（状態／抽選か／配信か）===\n')
for k, n in state.most_common():
    out.write('  %-8s %-4s %-4s %5d枠\n' % (k[0], k[1], k[2], n))
out.write('\n券種名(front_text)が有る %d枠 / 空 %d枠\n' % (hasname, noname))
out.write('締切(lottery_end_date)が有る %d枠 / 無い %d枠\n' % (hasend, noend))
out.write('価格が空 %d枠\n' % price_ng)
out.write('\n=== 1イベントあたりの券種数 ===\n')
for k, n in sorted(nticket.items()):
    out.write('  %2d券種 … %4d件\n' % (k, n))
out.write('\n=== venue_location（県が取れるか）上位20 ===\n')
for k, n in loc.most_common(20):
    out.write('  %-24s %4d件\n' % (k, n))

out.write('\n=== 券種名が取れている例 10件 ===\n')
c = 0
for u, e in det.items():
    for t in e.get('tickets') or []:
        if (t.get('name') or '').strip():
            out.write('  %-40s %s / %s %s / 締切%s %s\n'
                      % ((t['name'] or '')[:40], t.get('price'),
                         '抽選' if t.get('is_lottery') else '先着',
                         '配信' if t.get('is_stream') else '',
                         t.get('end_date'), t.get('end_time') or ''))
            c += 1
            break
    if c >= 10:
        break
out.close()
print('wrote tmp/x0921/zaiko_vocab.txt  details=%d' % len(det))
