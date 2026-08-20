"""heal --apply の前チェック。tmp/heal_stale.json の convert 結果と現在の index.html を比較し、
(1) 枠数の増減 (2) 現在あって新側で消える枠 (3) 消える枠に非ぴあURLが付いていないか を出す。
非ぴあ枠(e+/楽天/公式/リセール等)が消えるなら apply は危険＝手で守る。"""
import json
import re

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(const\s+EVENTS\s*=\s*)(\[.*?\])(;\s*\n)', h, re.S)
EVENTS = json.loads(m.group(2))
byid = {e['id']: e for e in EVENTS}

built = json.load(open('tmp/heal_stale.json', encoding='utf-8'))

def key(t):
    return (t.get('type') or '', t.get('date') or '', t.get('startDate') or '')

def is_pia(u):
    return 'pia.jp' in (u or '')

lines = []
danger = 0
for o in built:
    if o.get('status') != 'convert':
        lines.append(f"id={o['id']} status={o.get('status')} → 適用対象外")
        continue
    e = byid.get(o['id'])
    cur = e.get('tickets') or []
    new = o['tickets']
    curk = {key(t): t for t in cur}
    newk = {key(t): t for t in new}
    lost = [t for k, t in curk.items() if k not in newk]
    added = [t for k, t in newk.items() if k not in curk]
    lost_nonpia = [t for t in lost if t.get('url') and not is_pia(t.get('url'))]
    flag = ''
    if lost_nonpia:
        flag = '  🚨非ぴあ枠が消える'
        danger += 1
    lines.append(f"id={o['id']:<5} {(e.get('artist') or '')[:34]:<36} 枠 {len(cur)}→{len(new)} / 消える{len(lost)} 増える{len(added)}{flag}")
    for t in lost:
        u = t.get('url') or ''
        tag = 'ぴあ' if is_pia(u) else ('非ぴあ:' + u[:60] if u else 'URLなし(共通ボタン)')
        lines.append(f"      - 消: {t.get('type')} | date={t.get('date')} start={t.get('startDate')} | {tag}")
    for t in added:
        lines.append(f"      + 追: {t.get('type')} | date={t.get('date')} start={t.get('startDate')}")

lines.append('')
lines.append(f'=== 非ぴあ枠が消えるエントリ: {danger}件 ===')
open('tmp/heal_diff_0730.txt', 'w', encoding='utf-8').write('\n'.join(lines))
print('wrote tmp/heal_diff_0730.txt  danger=%d' % danger)
