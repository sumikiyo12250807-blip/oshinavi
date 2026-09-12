# -*- coding: utf-8 -*-
"""同じ名前の既存が2つあって保留した7件（tmp/built_same2_0912.json）の行き先を決めてファイルにする（読むだけ・tmpに書く）。
判断（2026-09-12 朝・ビルドした公演日と会場を既存と見比べた）:
  川崎鷹也 99301（茨城4/9・東京5/29）・99302（大阪5/27）＝2027年ツアーの別会場 → 4227（全国ツアー）へ
  NELKE 99303（石川6/13）・99304（宮城6/19）・99305（愛知7/7）・99306（大阪7/9）＝2027年ツアー → 4499 へ
    （99303 は 4499 に同じ一般発売の枠がすでにある＝足し込みの道具が同じ骨格として飛ばす）
  ガンバレ☆プロレス 99307（11/23 高島平）＝大会ごとに別エントリの形（5645・5646）→ 新規
出力: tmp/built_same2m_0912.json ＋ tmp/cand_same2m_0912.json（足す）／ tmp/new_same2_0912.json（新規）
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
MERGE = {99301: 4227, 99302: 4227, 99303: 4499, 99304: 4499, 99305: 4499, 99306: 4499}
NEW = {99307}
built = json.load(io.open('tmp/built_same2_0912.json', encoding='utf-8-sig'))
assert {b['id'] for b in built} == set(MERGE) | NEW, 'ビルド結果のidが想定と違う'
mb = [b for b in built if b['id'] in MERGE]
mc = [{'newid': b['id'], 'target': MERGE[b['id']], 'artist': b.get('artist'),
       'urls': [(b.get('links') or {}).get('pia')]} for b in mb]
nw = [b for b in built if b['id'] in NEW]
for p, d in (('tmp/built_same2m_0912.json', mb), ('tmp/cand_same2m_0912.json', mc), ('tmp/new_same2_0912.json', nw)):
    json.dump(d, io.open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('足す %d件（4227へ %d・4499へ %d）／ 新規 %d件'
      % (len(mb), sum(1 for v in MERGE.values() if v == 4227), sum(1 for v in MERGE.values() if v == 4499), len(nw)))
