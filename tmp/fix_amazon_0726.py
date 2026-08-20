# -*- coding: utf-8 -*-
"""改名した新着3件のAmazonリンクを現在の名前で作り直す（ビルダーのamazon()を使う＝手打ちしない）"""
import sys, io, re, json
sys.path.insert(0, 'tools')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from build_rakuten_entries import amazon

OLD_NEW = {
    3221: ('ケツメイシ［東京］', 'ケツメイシ'),
    3224: ('MATSURI［全国］', 'MATSURI'),
    3247: ('東京バレエ団 はじめてのバレエ「白鳥の湖」［東京］', '東京バレエ団 はじめてのバレエ「白鳥の湖」'),
}

path = 'index.html'
src = open(path, encoding='utf-8').read()
n = 0
for eid, (old, new) in OLD_NEW.items():
    old_url, new_url = amazon(old), amazon(new)
    if old_url not in src:
        print(f'  id{eid} 旧URLが見つからない（要確認）: {old_url}')
        continue
    c = src.count(old_url)
    src = src.replace(old_url, new_url)
    n += c
    print(f'  id{eid} 置換{c}箇所')
    print(f'    → {new_url}')
open(path, 'w', encoding='utf-8', newline='').write(src)
print(f'合計 {n}箇所 置換')
