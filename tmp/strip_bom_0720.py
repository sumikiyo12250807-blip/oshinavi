# -*- coding: utf-8 -*-
"""PowerShellのリダイレクトが付けるUTF-8 BOMを剥がして、JSONとして読めることを確認する。"""
import json
import sys

path = sys.argv[1] if len(sys.argv) > 1 else 'tmp/entries_0720.json'

with open(path, encoding='utf-8-sig') as f:
    data = json.load(f)

with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'{path}: BOM除去OK / {len(data)}件')
ids = [e.get('id') for e in data]
print(f'id範囲: {min(ids)}..{max(ids)}')
print(f'genre内訳: {json.dumps(dict(sorted(__import__("collections").Counter(e.get("genre") for e in data).items())), ensure_ascii=False)}')
print(f'_genre下書き: {json.dumps(dict(sorted(__import__("collections").Counter(e.get("_genre") for e in data).items())), ensure_ascii=False)}')
