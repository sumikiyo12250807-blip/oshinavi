# -*- coding: utf-8 -*-
"""ローチケ 9/21-9/27発売のうち未登録5件のURLを組む（2026-09-10）。
🚨gEntryMthd は data-rcptypename の値（[[reference_ltike_machine_unreachable]]）。
"""
import io
import json
import sys
from urllib.parse import quote

sys.stdout.reconfigure(encoding='utf-8')

# name | prfdate | venue | lcode | pfkeys | sn | carrier | venuecd | rcptypename
ROWS = [
    ('東京キューバンボーイズ　コンサート　２０２６　ｉｎ　Ｔｏｋｙｏ', '20261223', '新宿文化センター　大ホール',
     '71873', '20260904000002290127', '1', '08', '33375', '01'),
    ('岩崎宏美＆国府弘子', '20261226', '江津市総合市民センター',
     '62734', '20260703000002243050', '1', '08', '69371', '01'),
    ('長崎スタジアムシティ開業２周年記念　「ＨＡＰＰＩＮＥＳＳ　ＪＡＭ　２０２６」', '20261017', 'ＨＡＰＰＩＮＥＳＳ　ＡＲＥＮＡ',
     '82218', '20260820000002275623', '3', '08', '81620', '02'),
    ('星波', '20261018', '原宿ストロボカフェ',
     '70604', '20260727000002258553,20260727000002258557,20260727000002258554',
     '1', '08', '30723', '01'),
    ('歌声コンサート', '20261205', '滋賀県・野洲文化小劇場',
     '55628', '20260731000002263533', '1', '08', '51531', '01'),
]

out = []
for nm, d, v, lc, pk, sn, cc, bv, rc in ROWS:
    u = ('https://l-tike.com/order/?gLcode=' + lc
         + '&gPfKey=' + quote(pk, safe='')
         + '&gEntryMthd=' + rc + '&gScheduleNo=' + sn + '&gCarrierCd=' + cc
         + '&gPfName=' + quote(nm) + '&gBaseVenueCd=' + bv)
    out.append({'name': nm, 'date': d, 'venue': v, 'lcode': lc, 'sn': sn, 'url': u})
    print(nm[:34])
    print('  ' + u)

json.dump(out, io.open('tmp/ltike5_urls_0910.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('\n-> tmp/ltike5_urls_0910.json')
