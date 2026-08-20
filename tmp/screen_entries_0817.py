# -*- coding: utf-8 -*-
"""ビルドした新着エントリを投入前にふるいにかける。

🚨 落とすもの:
  ① 買える枠がゼロ（全枠が締切済み／取り込めなかった）
  ② 受付中しか無く、その締切が全部4日以内＝もうじき終わる
     （[[feedback_presale_first_harvest]]のコロラリー。発売前の枠を持つ子は残す）
  ③ 公演日が過去
"""
import json, io, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

TODAY = datetime.date.today()
LINE = TODAY + datetime.timedelta(days=4)
APPLY = '--apply' in sys.argv

# PowerShell の > リダイレクトは BOM 付き UTF-8 で書く。utf-8-sig で読まないと落ちる。
E = json.load(io.open('tmp/entries_0817.json', encoding='utf-8-sig'))
print('ビルド結果 %d件' % len(E))

keep, drop = [], []
for e in E:
    tks = e.get('tickets') or []
    alive = [t for t in tks if not t.get('soldout') and (t.get('date') or '9999') >= TODAY.isoformat()]
    presale = [t for t in alive if t.get('startDate') and t['startDate'] > TODAY.isoformat()]
    far = [t for t in alive if (t.get('date') or '') >= LINE.isoformat()]
    why = None
    if not tks:
        why = '枠が1つも取れなかった'
    elif not alive:
        why = '買える枠ゼロ（全部締切済み）'
    elif (e.get('date') or '9999') < TODAY.isoformat():
        why = '公演日が過去（%s）' % e.get('date')
    elif not presale and not far:
        why = 'もうじき終わる枠だけ（最終締切 %s）' % max((t.get('date') or '') for t in alive)
    if why:
        drop.append((e, why))
    else:
        keep.append(e)

print('\n=== 残す %d件 / 落とす %d件 ===' % (len(keep), len(drop)))
for e, why in drop:
    print('  落: id%-5s %-30s %s' % (e.get('id'), (e.get('artist') or '')[:28], why))

if APPLY:
    json.dump(keep, io.open('tmp/entries_0817_ok.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('\nwrote tmp/entries_0817_ok.json (%d件)' % len(keep))
else:
    print('\n（判定のみ。書き出すなら --apply）')
