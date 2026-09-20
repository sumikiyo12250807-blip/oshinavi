# -*- coding: utf-8 -*-
"""FANYのデータの「まとめ方」を確かめる＝event_id が同じ公演がいくつあるか、
買える枠／発売前の枠を持つ公演が何件あるか。エントリの畳み方を決めるため。
"""
import collections
import io
import json
import re
import sys

d = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'tmp/fany_0921.json', encoding='utf-8'))
perfs = d['performances']

LIVE = ('先着発売中', '抽選受付中')
PRE = ('先着発売前', '抽選受付前')

by_event = collections.defaultdict(list)
for p in perfs:
    by_event[p.get('event_id')].append(p)

sizes = collections.Counter(len(v) for v in by_event.values())
sellable, presale_only, dead = 0, 0, 0
for p in perfs:
    sts = {s.get('display_sales_status') for s in (p.get('performance_sales') or [])}
    if sts & set(LIVE):
        sellable += 1
    elif sts & set(PRE):
        presale_only += 1
    else:
        dead += 1

out = io.open('tmp/fany_group_survey.txt', 'w', encoding='utf-8')
out.write('公演 %d件 / イベント（event_id）%d本\n\n' % (len(perfs), len(by_event)))
out.write('=== 1イベントあたりの公演数 ===\n')
for k, n in sorted(sizes.items()):
    out.write('  %3d公演 … %5d本\n' % (k, n))
out.write('\n=== 公演の売り状態 ===\n')
out.write('  買える枠がある      %5d件\n' % sellable)
out.write('  発売前だけ          %5d件\n' % presale_only)
out.write('  終わった枠だけ      %5d件\n' % dead)

out.write('\n=== 公演が多いイベントの例（上位8本）===\n')
for eid, ps in sorted(by_event.items(), key=lambda x: -len(x[1]))[:8]:
    ps2 = sorted(ps, key=lambda p: p.get('performance_date') or '')
    out.write('event_id=%s  %d公演  %s\n' % (eid, len(ps), (ps2[0].get('name') or '')[:40]))
    for p in ps2[:4]:
        dt = re.sub(r'<[^>]+>', '', p.get('performance_date') or '')
        out.write('    %s  %s  枠%d  %s\n'
                  % (dt, (p.get('venue_name') or '')[:22],
                     len(p.get('performance_sales') or []),
                     '/'.join(sorted({s.get('display_sales_status')
                                      for s in (p.get('performance_sales') or [])}))))
    if len(ps) > 4:
        out.write('    … ほか%d公演\n' % (len(ps) - 4))

out.write('\n=== 同じ名前・同じ会場で公演日が違うもの（ツアーの形）上位5 ===\n')
by_nv = collections.defaultdict(set)
for p in perfs:
    by_nv[(p.get('name'), p.get('venue_name'))].add(
        re.sub(r'<[^>]+>', '', p.get('performance_date') or ''))
for (nm, vn), ds in sorted(by_nv.items(), key=lambda x: -len(x[1]))[:5]:
    out.write('  %-36s %-20s %d日\n' % ((nm or '')[:36], (vn or '')[:20], len(ds)))

out.write('\n=== 出す側らしい公演名（駐車・出店・エントリー）===\n')
pat = re.compile(r'委託販売|即売会|出店|ブース|エントリーフォーム|参加エントリ|駐車|案内登録')
hit = [p for p in perfs if pat.search((p.get('name') or '') )]
out.write('  公演名に当たり %d件\n' % len(hit))
for p in hit[:10]:
    out.write('    %s\n' % (p.get('name') or '')[:50])
hits2 = [s for p in perfs for s in (p.get('performance_sales') or [])
         if pat.search(s.get('sales_name') or '')]
out.write('  券種名に当たり %d枠\n' % len(hits2))
for s in hits2[:10]:
    out.write('    %s\n' % (s.get('sales_name') or '')[:50])
out.close()
print('wrote tmp/fany_group_survey.txt')
