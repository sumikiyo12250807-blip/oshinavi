# -*- coding: utf-8 -*-
# 11/17 早見優 27277（県=福岡・秋田／会場=福岡だけ／会期の表示に福岡だけ）と同じ型を数える
#   O＝県が2つ以上なのに会場が1つ（gate_fields の O と同じ物差し）・振り分け済みで公演がこれから
import io, re, sys, json, collections, datetime
sys.path.insert(0, 'C:/Users/user/oshinavi/tools')
import compact_events as C
T = datetime.date.today().isoformat()
E = C.load(io.open('C:/Users/user/oshinavi/index.html', encoding='utf-8', newline='').read())
O = [e for e in E if e.get('genre') != 'new' and (e.get('date') or '') >= T and '・' in (e.get('prefecture') or '')
     and '／' not in (e.get('venue') or '') and not (e.get('venue') or '').startswith('全国ツアー')]
vend = collections.Counter()
for e in O:
    us = ' '.join(t.get('url') or '' for t in e.get('tickets') or [])
    vend['ぴあ' if 'pia.jp' in us else 'e+' if 'eplus' in us else 'FANY' if 'fany' in us else 'TIGET' if 'tiget' in us else 'ほか'] += 1
out = ['O 既存 %d件 %s' % (len(O), dict(vend))]
for e in O[:40]:
    out.append('%s ｜県=%s ｜会場=%s ｜%s' % (e['id'], e.get('prefecture'), (e.get('venue') or '')[:30], (e.get('name') or '')[:30]))
json.dump([e['id'] for e in O], io.open('C:/Users/user/oshinavi/tmp/x1117/spot/O_ids.json', 'w'))
io.open('C:/Users/user/oshinavi/tmp/x1117/spot/count_O.txt', 'w', encoding='utf-8').write('\n'.join(out))
