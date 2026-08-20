# -*- coding: utf-8 -*-
"""オールスター紅白オペラ歌合戦(2904)をぴあ機械パースで再構築（適用はしない・中身確認用）"""
import sys, json
sys.path.insert(0, 'tools')
import build_pia_entries as B

cand = {
    'newid': 2904,
    'artist': 'オールスター 紅白オペラ歌合戦 2026',
    'name': 'オールスター 紅白オペラ歌合戦 2026',
    'urls': ['https://t.pia.jp/pia/event/event.do?eventCd=2623733'],
}
res = B.build(cand)
with open('tmp/opera_built.json', 'w', encoding='utf-8') as f:
    json.dump({'built': res, 'dropped': B._DROPPED}, f, ensure_ascii=False, indent=2)
