# -*- coding: utf-8 -*-
"""build入力から bundle の重複（中身が既存エントリと同じ窓）を外す"""
import io, json, sys
sys.stdout.reconfigure(encoding='utf-8')
BUNDLE_DUP = {25256: 8392, 25281: 25018, 25282: 24389, 25286: 25033, 25289: 23681, 25295: 22929, 25296: 22930, 25297: 22931}
c = json.load(open('tmp/x0928e/w/cands.json', encoding='utf-8'))
out = [x for x in c if x['newid'] not in BUNDLE_DUP]
json.dump(out, io.open('tmp/x0928e/w/build_in.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(out), '件をビルドへ／外した', len(c) - len(out))
