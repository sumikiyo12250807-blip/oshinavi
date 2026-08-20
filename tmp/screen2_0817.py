# -*- coding: utf-8 -*-
"""2本のビルド結果をふるいにかけて50件に揃える。落とす条件は screen_entries_0817.py と同じ。"""
import json, io, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

TODAY = datetime.date.today()
LINE = TODAY + datetime.timedelta(days=4)
APPLY = '--apply' in sys.argv
CAP = 50

E = []
for f in ('tmp/entries_0817.json', 'tmp/entries_0817d.json'):
    E += json.load(io.open(f, encoding='utf-8-sig'))

keep, drop = [], []
for e in E:
    tks = e.get('tickets') or []
    alive = [t for t in tks if not t.get('soldout') and (t.get('date') or '9999') >= TODAY.isoformat()]
    presale = [t for t in alive if t.get('startDate') and t['startDate'] > TODAY.isoformat()]
    far = [t for t in alive if (t.get('date') or '') >= LINE.isoformat()]
    why = None
    if not tks:
        why = '枠が取れなかった'
    elif not alive:
        why = '買える枠ゼロ'
    elif (e.get('date') or '9999') < TODAY.isoformat():
        why = '公演日が過去'
    elif not presale and not far:
        why = 'もうじき終わる枠だけ（最終締切 %s）' % max((t.get('date') or '') for t in alive)
    (drop if why else keep).append((e, why))

keep = [e for e, _ in keep]
over = keep[CAP:]
keep = keep[:CAP]
print('ビルド計 %d件 → 残す %d件 / 落とす %d件 / 50件超過で持ち越し %d件'
      % (len(E), len(keep), len(drop), len(over)))
for e, why in drop:
    print('  落: id%-5s %-28s %s' % (e.get('id'), (e.get('artist') or '')[:26], why))

if APPLY:
    json.dump(keep, io.open('tmp/entries_0817_ok.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('\nwrote tmp/entries_0817_ok.json (%d件)' % len(keep))
