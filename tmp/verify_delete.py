# -*- coding: utf-8 -*-
import re, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

src = open('index.html', encoding='utf-8').read()
m = re.search(r'const EVENTS\s*=\s*(\[.*?\]);\s*\n', src, re.S)
data = json.loads(m.group(1))  # ここで壊れてれば例外
print('JSONパースOK。EVENTS件数:', len(data))

deleted = {1072, 2589, 2596, 2598, 2654}
残 = [e['id'] for e in data if e['id'] in deleted]
print('削除対象で残ってるid:', 残 if 残 else 'なし（全削除確認）')

# NEW_ORDER 配列の中身
mo = re.search(r'const\s+NEW_ORDER\s*=\s*(\[[^\]]*\])', src)
if mo:
    no = json.loads(mo.group(1))
    zan = [i for i in no if i in deleted]
    print('NEW_ORDER件数:', len(no), '/ 削除idの残骸:', zan if zan else 'なし')
else:
    print('NEW_ORDER 見つからず')

# genre:new 件数（バッチ2確認）
print('genre:new 件数:', sum(1 for e in data if e.get('genre')=='new'))
