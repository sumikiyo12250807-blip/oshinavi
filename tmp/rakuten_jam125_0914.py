# -*- coding: utf-8 -*-
"""楽天の発売前ハーベストで未登録だった「@JAM PARTY vol.125」だけを build_rakuten_entries に渡す形で切り出す（読むだけ）。
使い方: python tmp/rakuten_jam125_0914.py
出力: tmp/rakuten_jam125_src_0914.json
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
pre = json.load(io.open('tmp/rakuten_presale.json', encoding='utf-8'))['presale']
rows = [p for p in pre if p['url'].rstrip('/').endswith('rtzppty')]
assert len(rows) == 1, '対象が1件でない %d' % len(rows)
json.dump(rows, io.open('tmp/rakuten_jam125_src_0914.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('切り出した: %s' % rows[0]['name'])
