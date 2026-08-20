# -*- coding: utf-8 -*-
"""7/2 発売前新着を index.html EVENTS 末尾に投入＋NEW_ORDER更新。
tmp/built_0702.json(build_pia_entries出力)を読み込む。JSON parse方式(今日の変換/削除と整合)。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

allnew = json.load(open('tmp/built_0702_final.json', encoding='utf-8'))
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

exist_ids = {e['id'] for e in EVENTS}
dup = [e['id'] for e in allnew if e['id'] in exist_ids]
assert not dup, 'ID衝突: %s' % dup

# eventCd二重チェック(既存と衝突する候補は投入しない=harvest dedupの保険)
ex_cd = set(re.findall(r'event(?:Bundle)?Cd=(\w+)', m.group(2)))
def cd_of(e):
    p = (e.get('links') or {}).get('pia') or ''
    mm = re.search(r'event(?:Bundle)?Cd=(\w+)', p)
    return mm.group(1) if mm else None
clash = [e['id'] for e in allnew if cd_of(e) in ex_cd]
if clash:
    print('⚠️ eventCd衝突 除外:', clash)
    allnew = [e for e in allnew if e['id'] not in clash]

EVENTS.extend(allnew)
new_ids = sorted(e['id'] for e in allnew)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
h2 = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]

no_new = '[' + ', '.join(str(i) for i in new_ids) + ']'
h2, n = re.subn(r'(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]', r'\g<1>' + no_new, h2, count=1)
assert n == 1, 'NEW_ORDER replaced=%d' % n

open('index.html.bak_0702_newpool', 'w', encoding='utf-8').write(h)
open('index.html', 'w', encoding='utf-8').write(h2)
print('投入 %d件 id%d..%d / NEW_ORDER更新 / 総数 %d → %d'
      % (len(allnew), new_ids[0], new_ids[-1], len(EVENTS) - len(allnew), len(EVENTS)))
