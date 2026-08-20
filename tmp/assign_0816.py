# -*- coding: utf-8 -*-
"""新着プール49件の振り分け（ユーザー明示OK 2026-08-16朝「新着振り分けて」）。
_genre をそのまま genre へ移し、_extraGenres は extraGenres へ。下書きキーは削除。NEW_ORDER は空に。
4296 みんなのアニソン・オーケストラ！ だけ extraGenres に anime を足す（アニソンで探す人が居るため）。
CRLF は heal_stale_deadlines と同じテキストモード書き戻しで維持。
"""
import re, json, sys, os
sys.stdout.reconfigure(encoding='utf-8')

APPLY = '--apply' in sys.argv
EXTRA_ADD = {4296: ['anime']}

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

moved = 0
for e in EVENTS:
    if e.get('genre') != 'new':
        continue
    g = e.get('_genre')
    if not g:
        print("⚠️ id%s は _genre が無い＝手当て要" % e['id']); continue
    ex = list(e.get('_extraGenres') or [])
    for a in EXTRA_ADD.get(e['id'], []):
        if a not in ex:
            ex.append(a)
    e['genre'] = g
    if ex:
        e['extraGenres'] = sorted(set((e.get('extraGenres') or []) + ex))
    for k in ('_genre', '_extraGenres', '_piaSub'):
        e.pop(k, None)
    moved += 1
    print("id%-5s → %-8s %s%s" % (e['id'], g, "+" + ",".join(ex) if ex else "", (e.get('artist') or '')[:30]))

print("振り分け %d件" % moved)
if not APPLY:
    print("（判定のみ。適用は --apply）"); sys.exit(0)

bak = 'index.html.bak_0816_assign'
if not os.path.exists(bak):
    open(bak, 'w', encoding='utf-8').write(h)

new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
h2 = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]

# NEW_ORDER を空配列に（振り分け済み＝新着タブは空になる）
m2 = re.search(r'(NEW_ORDER\s*=\s*)(\[.*?\])', h2, re.S)
if m2:
    h2 = h2[:m2.start()] + m2.group(1) + "[]" + h2[m2.end():]
    print("NEW_ORDER → [] にリセット")

open('index.html', 'w', encoding='utf-8').write(h2)
print("=== 適用完了 (backup: %s) ===" % bak)
