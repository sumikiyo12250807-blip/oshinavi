# -*- coding: utf-8 -*-
"""指定idのエントリを生JSONのまま出す（テンプレを写すため）。"""
import io, re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
h = io.open('index.html', encoding='utf-8', newline='').read()
evs = json.loads(re.search(r'const EVENTS = (\[.*?\]);\r?\n', h, re.S).group(1))
ids = [int(x) for x in sys.argv[1].split(',')]
for e in evs:
    if e['id'] in ids:
        print(json.dumps(e, ensure_ascii=False, indent=2))
print('--- 最大id =', max(e['id'] for e in evs))
m = re.search(r'const NEW_ORDER = (\[[^\]]*\])', h)
if m:
    arr = json.loads(m.group(1))
    print('NEW_ORDER 件数 =', len(arr), ' 末尾5 =', arr[-5:])
else:
    print('NEW_ORDER が見つからない')
