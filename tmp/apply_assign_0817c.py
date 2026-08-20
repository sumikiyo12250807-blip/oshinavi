# -*- coding: utf-8 -*-
"""新着プールの振り分けを適用する。
決定表 tmp/decision_0817c.json = {"assign": {"4426": "jpop", ...}, "hold": [4377, ...]}
 - assign にある id … genre を書き換え、_genre/_extraGenres/_piaSub を削除、NEW_ORDER から外す
 - hold にある id  … genre:"new" のまま据え置き（相談待ち）。_genre は下書きとして残す

🚨 CRLF保持（[[feedback_index_html_crlf_preserve]]）／並び順・id は動かさない
   （[[feedback_new_list_order_lock]]＝丸ごと作り直さない・id振り直し禁止）。

  python tmp/apply_assign_0817b.py [--apply]
"""
import io, re, sys, json
sys.stdout.reconfigure(encoding='utf-8')

APPLY = '--apply' in sys.argv
dec = json.load(io.open('tmp/decision_0817c.json', encoding='utf-8'))
ASSIGN = {int(k): v for k, v in dec['assign'].items()}
HOLD = set(dec.get('hold', []))

src = io.open('index.html', encoding='utf-8', newline='').read()
before_crlf = src.count('\r\n')
BLOCK = re.compile(r'  \{\r\n    "id": (\d+),.*?\r\n  \},?', re.S)

done, miss = [], []
for eid, genre in sorted(ASSIGN.items()):
    m = {int(x.group(1)): x for x in BLOCK.finditer(src)}.get(eid)
    if not m:
        miss.append((eid, 'エントリが無い')); continue
    seg = m.group(0)
    if '"genre": "new"' not in seg:
        cur = re.search(r'"genre": "([^"]*)"', seg)
        miss.append((eid, '既に genre=%s' % (cur.group(1) if cur else '?'))); continue
    seg2 = seg.replace('"genre": "new"', '"genre": "%s"' % genre, 1)
    # 下書きフィールドを消す（[[project_vendor_genre_autoassign]]＝適用後は削除して確定）
    seg2 = re.sub(r'    "_genre": "[^"]*",\r\n', '', seg2)
    seg2 = re.sub(r'    "_extraGenres": \[[^\]]*\],\r\n', '', seg2)
    seg2 = re.sub(r'    "_piaSub": "[^"]*",\r\n', '', seg2)
    src = src[:m.start()] + seg2 + src[m.end():]
    done.append((eid, genre))

mo = re.search(r'(const NEW_ORDER = )(\[[^\]]*\])', src)
order = [i for i in json.loads(mo.group(2)) if i not in ASSIGN]
src = src[:mo.start(2)] + json.dumps(order) + src[mo.end(2):]

print('=== 振り分け適用 %d件 ===' % len(done))
for eid, g in done:
    print('  id%-5d → %s' % (eid, g))
if miss:
    print('\n⚠️ 適用できなかった %d件:' % len(miss))
    for eid, why in miss:
        print('  id%-5d %s' % (eid, why))

EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S).group(2))
pool = [e['id'] for e in EV if e.get('genre') == 'new']
print('\nプールに残る %d件: %s' % (len(pool), pool))
print('NEW_ORDER %d件: %s' % (len(order), order))
print('照合: プール==NEW_ORDER →', '一致' if sorted(pool) == sorted(order) else '❌不一致')
print('hold指定 %s → 残っている: %s' % (sorted(HOLD), sorted(HOLD) == sorted(pool)))
left = [e['id'] for e in EV if e.get('_genre') and e.get('genre') != 'new']
print('下書き_genreの消し残り:', left or 'なし')
print('CRLF %d → %d ／ LF単独 %d' % (before_crlf, src.count('\r\n'), src.count('\n') - src.count('\r\n')))

if APPLY:
    io.open('index.html.bak_0817c_assign', 'w', encoding='utf-8', newline='').write(
        io.open('index.html', encoding='utf-8', newline='').read())
    io.open('index.html', 'w', encoding='utf-8', newline='').write(src)
    print('\n適用しました（backup: index.html.bak_0817c_assign）')
else:
    print('\n（判定のみ。適用するなら --apply）')

