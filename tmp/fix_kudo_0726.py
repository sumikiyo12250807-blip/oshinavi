# -*- coding: utf-8 -*-
"""工藤静香(id2300)をぴあ機械パースで再構築して中身を確認（適用はしない）"""
import sys, io, json
sys.path.insert(0, 'tools')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import build_pia_entries as B

cand = {
    'newid': 2300,
    'artist': '工藤静香',
    'name': '工藤静香',
    'urls': ['https://t.pia.jp/pia/event/event.do?eventBundleCd=b2667295'],
}
res = B.build(cand)
with open('tmp/kudo_built.json', 'w', encoding='utf-8') as f:
    json.dump({'built': res, 'dropped': B._DROPPED}, f, ensure_ascii=False, indent=2)
