# -*- coding: utf-8 -*-
"""楽天の「既存に足す」7件を、build_rakuten_entries で既存idのまま作り直す。

  python tmp/rakuten_addto_build_0910.py

出力＝tmp/built_rakuten_addto_0910.json（idは既存エントリのid）。
このあと tmp/add_missing_slots_0910.py で**（県・公演日・締切）**で突き合わせて足す
（券種名で突き合わせると二重登録になる＝[[feedback_capture_all_deadlines_on_add]]）。
"""
import io
import json
import sys
import time

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_harvest as RH
import build_rakuten_entries as B

addto = json.load(io.open('tmp/rakuten_presale_addto_0910.json', encoding='utf-8'))
out = []
for x in addto:
    try:
        rec = RH.parse_page(x['url'], RH.fetch(x['url']))
    except Exception as ex:
        print('  取得失敗 id=%s %r' % (x['id'], ex))
        continue
    e, why = B.build([rec], x['id'])
    if not e:
        print('  作れない id=%s (%s)' % (x['id'], why))
        continue
    e['id'] = x['id']
    out.append(e)
    print('  id=%-5s %-40s 枠%d' % (x['id'], (e.get('name') or '')[:40], len(e['tickets'])))
    for t in e['tickets']:
        print('        %s' % t['type'][:70])
    time.sleep(0.5)

json.dump(out, io.open('tmp/built_rakuten_addto_0910.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('\n作れた %d件 → tmp/built_rakuten_addto_0910.json' % len(out))
