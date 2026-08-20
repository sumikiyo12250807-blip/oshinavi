# -*- coding: utf-8 -*-
"""2周目チェックのお直し。
 1) 2885 アインシュタイン＝統合時に付けたラベルで県名が二重表示になっていた
 2) 2872 キノコホテル＝dateLabel に会場名が入っておらず他エントリと不揃い
"""
import re, json, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

PATH = 'index.html'
BAK = 'index.html.bak_0719_fix2'
shutil.copy(PATH, BAK)
h = open(PATH, encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
E = json.loads(m.group(2))
byid = {e['id']: e for e in E}

# 1) 二重ラベルを剥がす（「一般発売 （…）（…公演）」→「一般発売（…公演）」）
for t in byid[2885]['tickets']:
    before = t['type']
    t['type'] = re.sub(r'^一般発売\s*（[^）]*）(?=（)', '一般発売', before)
    if before != t['type']:
        print(f'[枠] {before!r}\n  → {t["type"]!r}')

# 2) dateLabel に会場名を足す
e = byid[2872]
before = e['dateLabel']
if e['venue'] not in before:
    e['dateLabel'] = before + ' ' + e['venue']
    print(f'[期間] {before!r}\n  → {e["dateLabel"]!r}')

new_arr = json.dumps(E, ensure_ascii=False, indent=2)
new_arr = '\n'.join(('  ' + ln if ln.strip() else ln) for ln in new_arr.split('\n')).lstrip()
h = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]
open(PATH, 'w', encoding='utf-8').write(h)
print(f'=== 書き戻し完了 (backup {BAK}) ===')
