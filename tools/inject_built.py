# -*- coding: utf-8 -*-
"""完成済みエントリをindex.htmlのEVENTS配列末尾に投入し、NEW_ORDERを投入id昇順で更新する。

  python tools/inject_built.py [entries.json]   （既定 tmp/all_new2.json）

EVENTS を JSON として読み→足す→書き戻す方式（heal_stale/dedup_badges と同一）。
旧版は行末アンカー '  }\\n];;;;;;;;' を文字列置換していたが、他ツールが json.dumps で
書き戻すとアンカーが消えて落ちるため廃止（2026-07-13）。
"""
import re, json, io, sys, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SRC_JSON = sys.argv[1] if len(sys.argv) > 1 else 'tmp/all_new2.json'
allnew = json.load(open(SRC_JSON, encoding='utf-8'))
h = open('index.html', encoding='utf-8').read()

m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
assert m, 'EVENTS配列が見つからない'
EVENTS = json.loads(m.group(2))

exist = {e['id'] for e in EVENTS}
dup = [e['id'] for e in allnew if e['id'] in exist]
assert not dup, 'id重複: %s' % dup[:10]

EVENTS.extend(allnew)

new_ids = sorted(e['id'] for e in allnew)
# NEW_ORDER は「既存の並びの後ろに追記」。上書きすると同日2回目の投入で前のバッチが
# 新着タブから消える（2026-07-13 Jリーグ5件の投入で87件分を飛ばした）。順序は投入順で固定
# （memory: feedback_new_list_order_lock / feedback_new_order_array）。
mo = re.search(r'(NEW_ORDER\s*=\s*)\[([0-9,\s]*)\]', h)
assert mo, 'NEW_ORDER が見つからない'
cur = [int(x) for x in re.findall(r'\d+', mo.group(2))]
merged = cur + [i for i in new_ids if i not in cur]
no_new = '[' + ', '.join(str(i) for i in merged) + ']'
h2, n = re.subn(r'(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]', r'\g<1>' + no_new, h, count=1)
assert n == 1, 'NEW_ORDER replaced=%d' % n
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h2, re.S)

bak = f'index.html.bak_{datetime.date.today():%m%d}_newpool'
open(bak, 'w', encoding='utf-8').write(h)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
open('index.html', 'w', encoding='utf-8').write(h2[:m.start()] + m.group(1) + new_arr + m.group(3) + h2[m.end():])
print('投入 %d件 id%d..%d / NEW_ORDER更新(%d件) / 総%d件 (backup %s)'
      % (len(allnew), new_ids[0], new_ids[-1], len(new_ids), len(EVENTS), bak))
