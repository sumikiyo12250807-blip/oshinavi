# -*- coding: utf-8 -*-
"""7/1 発売前新着50件を index.html EVENTS 末尾に投入＋NEW_ORDER更新。
apply/delete と同じ確実な正規表現方式（json.dumps indent=2 で全配列書き戻し）。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

allnew = json.load(open('tmp/all_new2.json', encoding='utf-8'))
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

exist_ids = {e['id'] for e in EVENTS}
dup = [e['id'] for e in allnew if e['id'] in exist_ids]
assert not dup, 'ID衝突: %s' % dup

EVENTS.extend(allnew)
new_ids = sorted(e['id'] for e in allnew)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
h2 = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]

no_new = '[' + ', '.join(str(i) for i in new_ids) + ']'
h2, n = re.subn(r'(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]', r'\g<1>' + no_new, h2, count=1)
assert n == 1, 'NEW_ORDER replaced=%d' % n

open('index.html.bak_0701_newpool', 'w', encoding='utf-8').write(h)
open('index.html', 'w', encoding='utf-8').write(h2)
print('投入 %d件 id%d..%d / NEW_ORDER更新 / 総数 %d → %d'
      % (len(allnew), new_ids[0], new_ids[-1], len(EVENTS) - len(allnew), len(EVENTS)))
