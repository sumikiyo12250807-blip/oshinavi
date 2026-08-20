# -*- coding: utf-8 -*-
"""五十嵐紅|ギターと静寂『クリスマス』の会場別4エントリを1ツアーに束ね直す下ごしらえ。
   4つのぴあURLをまとめて build に渡す（会場列挙＋各枠に会場別URLが付く）。
"""
import sys, json
sys.path.insert(0, 'tools')
import build_pia_entries as B

cand = {
    'newid': 3298,
    'artist': '五十嵐紅',
    'name': '五十嵐紅|ギターと静寂『クリスマス』',
    'urls': [
        'https://t.pia.jp/pia/event/event.do?eventCd=2627949',  # 千葉 12/7
        'https://t.pia.jp/pia/event/event.do?eventCd=2627951',  # 東京 12/13
        'https://t.pia.jp/pia/event/event.do?eventCd=2627955',  # 下関 12/18
        'https://t.pia.jp/pia/event/event.do?eventCd=2627935',  # 倉敷 12/22
    ],
}
out = {}
try:
    out['built'] = B.build(cand)
except Exception as ex:
    out['error'] = repr(ex)[:300]
out['dropped'] = B._DROPPED
json.dump(out, open('tmp/igarashi_merge.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=2)
