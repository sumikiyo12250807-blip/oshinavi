# -*- coding: utf-8 -*-
"""投入前の重複チェック＝eventCd/eventBundleCd と正規化名で既存とぶつからないか
   （memory: feedback_harvest_dedup_check）"""
import sys, io, re, json, unicodedata
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def cds(e):
    s = json.dumps(e, ensure_ascii=False)
    return set(re.findall(r'event(?:Bundle)?Cd=(\w+)', s))


def norm(s):
    s = unicodedata.normalize('NFKC', s or '').lower()
    return re.sub(r'[\s　・,，.。!！?？"\'（）\(\)\[\]「」『』【】~〜\-–—]', '', s)


src = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'const EVENTS = (\[.*?\n\s*\]);', src, re.S)
existing = json.loads(m.group(1))
# PowerShell の > リダイレクトは BOM を付けるので utf-8-sig で読む
built = json.load(open('tmp/built_0727.json', encoding='utf-8-sig'))

ex_cd = {}
for e in existing:
    for c in cds(e):
        ex_cd.setdefault(c, e)
ex_name = {}
for e in existing:
    ex_name.setdefault(norm(e.get('name')), e)

hit_cd, hit_name = [], []
for b in built:
    for c in cds(b):
        if c in ex_cd:
            hit_cd.append((b['id'], b['name'], c, ex_cd[c]['id'], ex_cd[c]['name']))
    n = norm(b.get('name'))
    if n in ex_name:
        hit_name.append((b['id'], b['name'], ex_name[n]['id'], ex_name[n]['name']))

print(f'構築 {len(built)}件')
print(f'\n=== eventCd かぶり {len(hit_cd)}件 ===')
for r in hit_cd:
    print(f'  新id{r[0]} {r[1][:34]} | cd={r[2]} → 既存id{r[3]} {r[4][:34]}')
print(f'\n=== 正規化名かぶり {len(hit_name)}件 ===')
for r in hit_name:
    print(f'  新id{r[0]} {r[1][:34]} → 既存id{r[2]} {r[3][:34]}')
if not hit_cd and not hit_name:
    print('\n重複なし＝投入OK')
