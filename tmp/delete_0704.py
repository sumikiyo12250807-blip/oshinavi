# -*- coding: utf-8 -*-
"""7/4 削除実行: 期限切れ削除候補15件を index.html から除去。
二段構え(build⇄reconcile)で 0=0 一致確認済みのぴあ14件 + eplus 81(WebFetch「受付全終了」確認)。
82(東京女子プロレス)=本日7/4公演のため今日は残す(翌朝削除)。
115 FRUITS ZIPPER=大型ツアーだがWebFetch「現在販売中のチケット情報はありません」全枠終了確認。
[[feedback_user_confirms_expired]]の完全自走方針(2026-07-04)。EVENTS は json.dumps(indent=2) 形式。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# pia二段構え0=0一致14件 + eplus 81(WebFetch確認)
DEL = set([115, 570, 255, 306, 531, 556, 699, 852, 1235, 1349,
           1529, 1710, 1713, 1720, 81])

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
open('index.html.bak_0704_morning_delete', 'w', encoding='utf-8').write(h)
h2 = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]
open('index.html', 'w', encoding='utf-8').write(h2)
print("✅ 削除完了 (backup: index.html.bak_0704_morning_delete)")
