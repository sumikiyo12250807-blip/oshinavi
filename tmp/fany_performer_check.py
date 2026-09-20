# -*- coding: utf-8 -*-
"""同じ event_id の公演で出演者（performer_detail）が日替わりかを確かめる。
畳むか公演ごとに分けるかの判断材料（畳むと出演者が壊れるなら分ける）。
"""
import collections, io, json, re, sys

d = json.load(open('tmp/fany_0921.json', encoding='utf-8'))
by = collections.defaultdict(list)
for p in d['performances']:
    by[p.get('event_id')].append(p)

out = io.open('tmp/fany_performer_check.txt', 'w', encoding='utf-8')
multi = {k: v for k, v in by.items() if len(v) > 1}
same, diff = 0, 0
for k, v in multi.items():
    if len({(p.get('performer_detail') or '').strip() for p in v}) == 1:
        same += 1
    else:
        diff += 1
out.write('公演が2つ以上のイベント %d本\n' % len(multi))
out.write('  出演者が全公演で同じ  %d本\n' % same)
out.write('  出演者が公演ごとに違う %d本\n\n' % diff)

out.write('=== 出演者が日替わりの例（大きいもの3本）===\n')
for k, v in sorted(multi.items(), key=lambda x: -len(x[1]))[:3]:
    names = {(p.get('performer_detail') or '')[:60] for p in v}
    out.write('event_id=%s %d公演 %s／出演者のパターン %d通り\n'
              % (k, len(v), (v[0].get('name') or '')[:26], len(names)))
    for p in sorted(v, key=lambda x: x.get('performance_date') or '')[:3]:
        dt = re.sub(r'<[^>]+>', '', p.get('performance_date') or '')
        out.write('   %s %s 出演=%s\n' % (dt, p.get('open_start_time_text'),
                                        (p.get('performer_detail') or '（空）')[:70]))
out.write('\n=== 出演者が空の公演 ===\n')
empty = [p for p in d['performances'] if not (p.get('performer_detail') or '').strip()]
out.write('  %d件 / %d件\n' % (len(empty), len(d['performances'])))
for p in empty[:5]:
    out.write('   %s @ %s\n' % ((p.get('name') or '')[:40], p.get('venue_name')))
out.write('\n=== 同じ日・同じ会場・同じイベントで2公演以上（時刻で分かれる）===\n')
cnt = collections.Counter()
for p in d['performances']:
    dt = re.sub(r'<[^>]+>', '', p.get('performance_date') or '')
    cnt[(p.get('event_id'), dt, p.get('venue_id'))] += 1
dup = {k: v for k, v in cnt.items() if v > 1}
out.write('  %d組（例）\n' % len(dup))
for k, v in list(dup.items())[:5]:
    ps = [p for p in d['performances']
          if p.get('event_id') == k[0] and p.get('venue_id') == k[2]
          and re.sub(r'<[^>]+>', '', p.get('performance_date') or '') == k[1]]
    out.write('   event=%s %s %d公演: %s\n'
              % (k[0], k[1], v, ' / '.join((p.get('open_start_time_text') or '?') for p in ps)))
out.close()
print('wrote tmp/fany_performer_check.txt')
