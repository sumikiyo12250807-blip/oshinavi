# -*- coding: utf-8 -*-
"""ローチケの data-* 属性から個別公演URLを組み立てる（2026-09-10）。
[[reference_ltike_machine_unreachable]] の形：
https://l-tike.com/order/?gLcode=..&gPfKey=..&gEntryMthd=02&gScheduleNo=..&gCarrierCd=..&gPfName=..&gBaseVenueCd=..
🚨組み立てただけでは載せない＝実ブラウザで開いて立つか確認する。
"""
import io
import json
import sys
from urllib.parse import quote

sys.stdout.reconfigure(encoding='utf-8')

# prfname|prfdate|venue|lcode|pfkeys|schduleno|carrier|basevenuecd
ROWS = [
    ('別府葉子', '20261219', '国際楽器社ホール', '55384', '20260908000002291683', '1', '08', '53158'),
    ('野田かつひこ', '20261215', '石橋文化ホール', '82465', '20260907000002290717', '1', '08', '81776'),
    ('ＲＥＶＥＲＳＥ　ＥＤＧＥ　２', '20261102', 'ＳＵＰＥＲＮＯＶＡ　ＫＡＷＡＳＡＫＩ', '72049', '20260831000002286720', '1', '08', '34027'),
    ('ＲＥＶＥＲＳＥ　ＥＤＧＥ　２', '20261102', 'ＳＵＰＥＲＮＯＶＡ　ＫＡＷＡＳＡＫＩ', '72049', '20260831000002286720', '2', '08', '34027'),
]

out = []
for nm, d, v, lc, pk, sn, cc, bv in ROWS:
    u = ('https://l-tike.com/order/?gLcode=%s&gPfKey=%s&gEntryMthd=02&gScheduleNo=%s'
         '&gCarrierCd=%s&gPfName=%s&gBaseVenueCd=%s' % (lc, pk, sn, cc, quote(nm), bv))
    out.append({'name': nm, 'date': d, 'venue': v, 'lcode': lc, 'sn': sn, 'url': u})
    print('%s  sn=%s' % (nm, sn))
    print('  ' + u)

json.dump(out, io.open('tmp/ltike_urls_0910.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('\n-> tmp/ltike_urls_0910.json')
