# -*- coding: utf-8 -*-
"""harvest出力(受付中)→build候補へ整形。eventCd重複を既存DB＆バッチ内で除外し、
先頭N件にtemp newidを振って tmp/cands_0628.json を出力。"""
import re, json, io, sys, unicodedata
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
N = int(sys.argv[1]) if len(sys.argv) > 1 else 65

harv = json.load(open('tmp/harvest_0628_uketsuke.json', encoding='utf-8'))
cands_raw = harv['new']
idx = open('index.html', encoding='utf-8').read()

def ecd(u):
    m = re.search(r'event(?:Bundle)?Cd=(\w+)', u or '')
    return m.group(1) if m else None

existing_ecd = set(re.findall(r'event(?:Bundle)?Cd=(\w+)', idx))
def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　・／/＜＞<>「」『』（）()【】’\'"!！\-—]', '', s).lower()
ex_names = set(norm(m) for m in re.findall(r'"(?:artist|name)"\s*:\s*"([^"]+)"', idx))

picked, seen_ecd, skip_dup = [], set(), 0
for it in cands_raw:
    e = ecd(it['url'])
    if not e: continue
    if e in existing_ecd or e in seen_ecd:
        skip_dup += 1; continue
    nm = norm(it['artist'])
    if nm and (nm in ex_names or any((nm in en or en in nm) for en in ex_names if len(en) > 3 and len(nm) > 3)):
        skip_dup += 1; continue
    seen_ecd.add(e)
    picked.append(it)
    if len(picked) >= N: break

cands = [{'newid': i, 'artist': it['artist'], 'urls': [it['url']]} for i, it in enumerate(picked)]
json.dump(cands, open('tmp/cands_0628.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f"harvest new={len(cands_raw)} / eventCd重複・名前重複skip={skip_dup} / 採用候補={len(cands)}")
for c in cands[:len(cands)]:
    print(f"  temp{c['newid']:2d} {c['artist'][:30]} | {c['urls'][0][-30:]}")
