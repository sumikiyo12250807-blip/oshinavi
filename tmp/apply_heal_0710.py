# -*- coding: utf-8 -*-
"""heal_hidden_0710.json を index.html に適用。
tickets のみ置換（venue/dateLabel は過去のQC手修正を巻き戻さないため据え置き）。
status=delete は触らない（ユーザーOK後に別途削除）。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DRY = '--apply' not in sys.argv
TODAY = '2026-07-10'
built = {o['id']: o for o in json.load(open('tmp/heal_hidden_0710.json', encoding='utf-8'))}
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

def hidden(t):
    sd, d = t.get('startDate'), t.get('date')
    return bool(sd and sd == d and d <= TODAY and not t.get('saleUntilSoldOut'))

changed = 0; before_h = 0; after_h = 0
for e in EVENTS:
    o = built.get(e.get('id'))
    if not o or o.get('status') != 'convert':
        continue
    if not o.get('tickets'):
        print('SKIP empty', e['id']); continue
    before_h += sum(1 for t in e.get('tickets', []) if hidden(t))
    e['tickets'] = o['tickets']
    after_h += sum(1 for t in o['tickets'] if hidden(t))
    changed += 1
print(f"=== convert {changed}件 適用 / 隠れ枠 {before_h} → {after_h} ===")
if DRY:
    print("(DRY)")
else:
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open('index.html.bak_0710_heal_hidden','w',encoding='utf-8').write(h)
    open('index.html','w',encoding='utf-8').write(h[:m.start()]+m.group(1)+new_arr+m.group(3)+h[m.end():])
    print("written (backup: index.html.bak_0710_heal_hidden)")
