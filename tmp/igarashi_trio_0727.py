# -*- coding: utf-8 -*-
"""五十嵐紅トリオ|クリスマス 2026 の会場別5エントリを1ツアーに束ね直す下ごしらえ。"""
import sys, json
sys.path.insert(0, 'tools')
import build_pia_entries as B

cand = {
    'newid': 3303,
    'artist': '五十嵐紅トリオ|クリスマス 2026',
    'name': '五十嵐紅トリオ|クリスマス 2026',
    'urls': [
        'https://t.pia.jp/pia/event/event.do?eventCd=2627940',  # 東京 12/2
        'https://t.pia.jp/pia/event/event.do?eventCd=2627945',  # みなとみらい 12/9
        'https://t.pia.jp/pia/event/event.do?eventCd=2627962',  # 福岡 12/19
        'https://t.pia.jp/pia/event/event.do?eventCd=2627932',  # 名古屋 12/20
        'https://t.pia.jp/pia/event/event.do?eventCd=2627938',  # 大阪 12/23
    ],
}
out = {}
try:
    out['built'] = B.build(cand)
except Exception as ex:
    out['error'] = repr(ex)[:300]
out['dropped'] = B._DROPPED
json.dump(out, open('tmp/igarashi_trio.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=2)
