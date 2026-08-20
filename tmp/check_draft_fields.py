# -*- coding: utf-8 -*-
import re, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

src = open('index.html', encoding='utf-8').read()
m = re.search(r'const EVENTS\s*=\s*(\[.*?\]);\s*\n', src, re.S)
data = json.loads(m.group(1))

assigned = [e for e in data if e.get('genre') != 'new']  # 振り分け済み
newp = [e for e in data if e.get('genre') == 'new']

def cnt(lst, key):
    return sum(1 for e in lst if key in e and e.get(key) not in (None, ''))

print('振り分け済みエントリ:', len(assigned))
print('  _genre を残してる数:', cnt(assigned, '_genre'))
print('  _piaSub を残してる数:', cnt(assigned, '_piaSub'))
print()
print('新着(genre:new):', len(newp))
print('  _genre 保持:', cnt(newp, '_genre'), '/ _piaSub 保持:', cnt(newp, '_piaSub'))
