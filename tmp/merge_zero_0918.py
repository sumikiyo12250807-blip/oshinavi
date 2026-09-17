# -*- coding: utf-8 -*-
# 取り直した枠を既存エントリへ「足し算」で入れる
#   ・売り切れ／販売終了の印が付いた枠は残す（画面に出ているので消さない）
#   ・取り直した枠と同じ券種名（日付部分を落として比較）の古い枠だけ外す
#   ・それ以外の既存枠はそのまま残す
import re, json, io

cands = json.load(open('tmp/cands_zero_0918.json', encoding='utf-8'))
tgt = {x['newid']: x['target'] for x in cands}
built = json.load(open('tmp/built_zero_0918.json', encoding='utf-8'))

h = open('index.html', encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
by = {e['id']: e for e in EVENTS}


def base(s):
    s = re.sub(r'〜?\s*\d{1,2}/\d{1,2}\s*\d{0,2}:?\d{0,2}\s*(発売)?\s*$', '', s or '')
    return s.strip()


log = io.open('tmp/merge_zero_0918.txt', 'w', encoding='utf-8')
n = 0
for b in built:
    t = tgt.get(b['id'])
    e = by.get(t)
    if not e:
        log.write(f"target{t} が無い\n")
        continue
    old = e.get('tickets') or []
    newt = b.get('tickets') or []
    newbase = {base(x.get('type')) for x in newt}
    keep = [x for x in old if x.get('soldout') or x.get('saleEnded')]
    keep += [x for x in old if not (x.get('soldout') or x.get('saleEnded'))
             and base(x.get('type')) not in newbase]
    log.write(f"id{t} {e.get('artist','')[:36]}: 旧{len(old)}枠 → 取り直し{len(newt)}＋据置{len(keep)}枠\n")
    for x in newt:
        log.write(f"   ＋ {x.get('type','')[:62]} | date={x.get('date')}\n")
    for x in keep:
        log.write(f"   ＝ {x.get('type','')[:62]} | date={x.get('date')} | sold={x.get('soldout')}\n")
    e['tickets'] = list(newt) + keep
    n += 1
log.write(f"\n{n}件に適用\n")
log.close()

new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
open('index.html', 'w', encoding='utf-8', newline='').write(
    h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print('ok', n)
