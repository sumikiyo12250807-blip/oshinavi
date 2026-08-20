# -*- coding: utf-8 -*-
"""ドラゴンクエスト アイランドの4分割(2823/2824/2825/2957)を1エントリに束ね直す下ごしらえ。
   4つのぴあURLをまとめて build_pia_entries に渡し、券種が区別できる形で取れるか確認する。
"""
import sys, json
sys.path.insert(0, 'tools')
import build_pia_entries as B

URLS = [
    'https://t.pia.jp/pia/event/event.do?eventCd=2628482',  # ゴールド
    'https://t.pia.jp/pia/event/event.do?eventCd=2628484',  # プレミアムオールインワン
    'https://t.pia.jp/pia/event/event.do?eventCd=2628477',  # ライト
    'https://t.pia.jp/pia/event/event.do?eventCd=2628483',  # プレミアム
]
cand = {
    'newid': 2823,
    'artist': 'ドラゴンクエスト アイランド',
    'name': 'ドラゴンクエスト アイランド',
    'urls': URLS,
}
out = {}
try:
    out['built'] = B.build(cand)
except Exception as ex:
    out['error'] = repr(ex)[:300]
out['dropped'] = B._DROPPED
with open('tmp/dq_merge.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
