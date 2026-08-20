# -*- coding: utf-8 -*-
"""空カッコ会場3件を、直したビルダーで作り直して venue/dateLabel を確認する"""
import sys, json
sys.path.insert(0, 'tools')
import build_pia_entries as B

CANDS = [
    {'newid': 3272, 'artist': 'AARON', 'name': 'AARON',
     'urls': ['https://t.pia.jp/pia/event/event.do?eventCd=2628891']},
    {'newid': 3285, 'artist': 'ルシファー吉岡ネタライブ2026', 'name': 'ルシファー吉岡ネタライブ2026',
     'urls': ['https://t.pia.jp/pia/event/event.do?eventCd=2629085']},
    {'newid': 3286, 'artist': 'ナイツお笑いライブ', 'name': 'ナイツお笑いライブ',
     'urls': ['https://t.pia.jp/pia/event/event.do?eventCd=2626459']},
]
out = {}
for c in CANDS:
    try:
        out[c['newid']] = B.build(c)
    except Exception as ex:
        out[c['newid']] = {'error': repr(ex)[:300]}
json.dump({'built': out, 'dropped': B._DROPPED},
          open('tmp/revenue.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
