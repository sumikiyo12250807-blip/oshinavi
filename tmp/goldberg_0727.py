# -*- coding: utf-8 -*-
"""ゴルトベルク変奏曲2027 の大阪/岡山2件を1ツアーに束ね直す下ごしらえ"""
import sys, json
sys.path.insert(0, 'tools')
import build_pia_entries as B

cand = {
    'newid': 2841,
    'artist': 'ゴルトベルク変奏曲2027',
    'name': 'ゴルトベルク変奏曲2027',
    'urls': [
        'https://t.pia.jp/pia/event/event.do?eventCd=2627096',  # 大阪 1/10
        'https://t.pia.jp/pia/event/event.do?eventCd=2627097',  # 岡山 1/11
    ],
}
out = {}
try:
    out['built'] = B.build(cand)
except Exception as ex:
    out['error'] = repr(ex)[:300]
out['dropped'] = B._DROPPED
json.dump(out, open('tmp/goldberg.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=2)
