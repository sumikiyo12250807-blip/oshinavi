# -*- coding: utf-8 -*-
"""削除してしまった19件を元に戻す(ユーザーチェック前に消したミスの修復)。
delete前backup(bak_0709_morning_delete)から該当19件を取り出し、現index.htmlに復元。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DEL = [138,157,402,878,957,1316,1320,1326,1330,1448,1588,1589,1646,1662,1687,1732,1846,1897,887]
DRY = '--apply' not in sys.argv

bak = open('index.html.bak_0709_morning_delete', encoding='utf-8').read()
BAK_EVENTS = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);', bak, re.S).group(1))
bakid = {e['id']: e for e in BAK_EVENTS}

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
present = {e['id'] for e in EVENTS}

restored = []
for i in DEL:
    if i in present:
        print('  already present, skip', i); continue
    e = bakid.get(i)
    if not e:
        print('  !! NOT in backup', i); continue
    EVENTS.append(e)
    restored.append(i)

print(f"=== 復元 {len(restored)}/{len(DEL)} (total {len(present)} -> {len(EVENTS)}) ===")
print('  restored:', restored)
if DRY:
    print('(DRY)')
else:
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open('index.html.bak_0709_before_restore', 'w', encoding='utf-8').write(h)
    open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
    print('written (backup: index.html.bak_0709_before_restore)')
