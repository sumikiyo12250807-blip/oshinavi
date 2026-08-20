# -*- coding: utf-8 -*-
"""PowerShellのリダイレクトが付けたUTF-8 BOMを剥がす。"""
import io
import json
import sys

p = sys.argv[1]
d = json.load(io.open(p, encoding='utf-8-sig'))
json.dump(d, io.open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('stripped BOM: %s  items=%d' % (p, len(d)))
