# -*- coding: utf-8 -*-
"""7/3 削除実行: 期限切れ削除候補15件を index.html から除去。
ぴあ0枠=本物終了11件(A)+大物先行のみ終了/一般未発表4件(B)+公演中止1(877はA末尾)。
reconcile 0=0 一致で確認済み。877=WebFetch「この公演は中止」確認。
ユーザーOK「削除」(2026-07-03)。EVENTS は json.dumps(indent=2) 形式で書き戻す。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DEL = set([63, 291, 348, 431, 451, 501, 662, 1136, 1206, 1255,
           1353, 1428, 1445, 1524, 877])

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

before = len(EVENTS)
gone = [e['id'] for e in EVENTS if e['id'] in DEL]
kept = [e for e in EVENTS if e['id'] not in DEL]
missing = DEL - set(gone)
print(f"削除対象{len(DEL)} / 実削除{len(gone)} / DB未在{sorted(missing)}")
print(f"件数 {before} → {len(kept)}")

new_arr = json.dumps(kept, ensure_ascii=False, indent=2)
open('index.html.bak_0703_morning_delete', 'w', encoding='utf-8').write(h)
h2 = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]
open('index.html', 'w', encoding='utf-8').write(h2)
print("✅ 削除完了 (backup: index.html.bak_0703_morning_delete)")
