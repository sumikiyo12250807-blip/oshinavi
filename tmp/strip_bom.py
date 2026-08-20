# -*- coding: utf-8 -*-
"""PowerShell の > リダイレクトが付ける UTF-8 BOM を落とす（json.load が読めなくなる）。
使い方: python tmp/strip_bom.py <file> [...]"""
import json
import sys

for p in sys.argv[1:]:
    raw = open(p, 'rb').read()
    if raw.startswith(b'\xef\xbb\xbf'):
        raw = raw[3:]
        open(p, 'wb').write(raw)
        print(f'{p}: BOM除去')
    else:
        print(f'{p}: BOMなし')
    d = json.loads(raw.decode('utf-8'))
    print(f'   JSON OK  要素数={len(d)}')
