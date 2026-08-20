# -*- coding: utf-8 -*-
"""ヒール適用前の枠差分チェック（減る子を精査）"""
import json, re, io, sys

HEAL = 'tmp/heal_stale.json'
IDX = 'index.html'

heal = json.load(io.open(HEAL, encoding='utf-8'))
if isinstance(heal, dict):
    items = heal.get('items') or heal.get('convert') or list(heal.values())
else:
    items = heal

raw = io.open(IDX, encoding='utf-8', newline='').read()

def cur_tickets(eid):
    """index.html から id=eid のエントリの tickets を素朴に抜く"""
    m = re.search(r'\n\s*\{\s*"id":\s*%d\b' % eid, raw)
    if not m:
        return None
    start = m.start()
    # 次のエントリ開始 or 配列終端まで
    m2 = re.search(r'\n\s*\{\s*"id":\s*\d+\b', raw[start+5:])
    end = start+5+m2.start() if m2 else start+40000
    blk = raw[start:end]
    return re.findall(r'"type":\s*"([^"]*)"[^}]*?"date":\s*"([^"]*)"', blk)

for it in items:
    eid = it.get('id') if isinstance(it, dict) else None
    if eid is None:
        continue
    new = it.get('tickets') or []
    old = cur_tickets(int(eid))
    print('--- id=%s  現行%s枠 → 新%s枠' % (eid, len(old) if old is not None else '?', len(new)))
    if old is None:
        continue
    if len(new) >= len(old):
        continue
    print('  [現行]')
    for t, d in old:
        print('    %s | %s' % (d, t))
    print('  [新]')
    for t in new:
        print('    %s | %s' % (t.get('date'), t.get('type')))
