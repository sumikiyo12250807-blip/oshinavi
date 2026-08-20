# -*- coding: utf-8 -*-
"""tmp/convert_0629.json の status=convert を index.html に適用。
各エントリの tickets と date(イベント日=最終公演) のみ更新。dateLabel/venue/
prefecture/genre/links 等は据え置き(チャーン最小化)。delete は別途ユーザーOK後。
EVENTS は json.dumps(indent=2,ensure_ascii=False) 形式・キー順保持で書き戻す。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DRY = '--apply' not in sys.argv

prop = json.load(open('tmp/convert_0629.json', encoding='utf-8'))
conv = {o['id']: o for o in prop if o['status'] == 'convert'}

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
arr_text = m.group(2)
EVENTS = json.loads(arr_text)

changed = 0
for e in EVENTS:
    o = conv.get(e.get('id'))
    if not o:
        continue
    if not o['tickets']:
        print(f"  ⏭ SKIP id={e['id']} {e.get('artist','')[:24]} = 構築ticket空(要個別WebFetch)")
        continue
    old_n = len(e.get('tickets', []))
    e['tickets'] = o['tickets']
    e['date'] = o['date']
    changed += 1
    print(f"  id={e['id']} {e.get('artist','')[:24]} tickets {old_n}→{len(o['tickets'])} date→{o['date']}")

print(f"\n=== convert適用 {changed}/{len(conv)} 件 ===")

if DRY:
    print("(DRY-RUN: --apply で書き込み)")
else:
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open('index.html.bak_0629_morning_convert', 'w', encoding='utf-8').write(h)
    h2 = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]
    open('index.html', 'w', encoding='utf-8').write(h2)
    print("✅ index.html 書き込み完了 (backup: index.html.bak_0629_morning_convert)")
