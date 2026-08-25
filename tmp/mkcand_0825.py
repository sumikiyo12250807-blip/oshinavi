# -*- coding: utf-8 -*-
"""投入候補（発売前51＋受付中49＝100件）を build_pia_entries 用の形にする。
🚨投入前に「既存と同じ興行でないか」を緩い部分一致でも見る
   （完全一致だけだと『アンジュルム 2026秋…』のような型を見逃す＝2026-08-23の恒久化）。"""
import json, io, re, sys, unicodedata
sys.stdout.reconfigure(encoding='utf-8')

rows = []
for p in ('tmp/pick_0825.json', 'tmp/pick2_0825.json'):
    rows += json.load(io.open(p, encoding='utf-8'))
print('候補 %d件' % len(rows))

idx = io.open('index.html', encoding='utf-8').read()


def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　・／/＜＞<>「」『』（）()【】’\'"!！\-—~〜]', '', s).lower()


ex_names = set()
for m in re.finditer(r'"(?:artist|name)"\s*:\s*"([^"]+)"', idx):
    ex_names.add(norm(m.group(1)))
ex_cds = set(re.findall(r'event(?:Bundle)?Cd=(\w+)', idx))

# 次のid
ids = [int(m.group(1)) for m in re.finditer(r'"id":\s*(\d+)', idx)]
nid = max(ids) + 1
print('次のid = %d' % nid)

loose, dup, out = [], [], []
for it in rows:
    cd = it['_cd']
    if cd in ex_cds:
        dup.append((it['artist'], 'eventCd既出'))
        continue
    k = norm(it['artist'])
    hit = None
    if k in ex_names:
        hit = '完全一致'
    else:
        # 既存名が候補名に含まれる／候補名が既存名に含まれる（3文字以上の名前だけ見る）
        for en in ex_names:
            if len(en) >= 4 and (en in k or (len(k) >= 4 and k in en)):
                hit = '部分一致(%s)' % en[:20]
                break
    if hit:
        loose.append((it['artist'], hit, it['url']))
        continue
    out.append({'newid': nid, 'artist': it['artist'], 'urls': [it['url']]})
    nid += 1

print('\neventCd既出で除外: %d件' % len(dup))
print('🚨同じ興行の疑い（統合に回す）: %d件' % len(loose))
for a, why, u in loose[:25]:
    print('   %-38s %s' % (a[:36], why))
if len(loose) > 25:
    print('   … 他 %d件' % (len(loose) - 25))
print('\n投入する: %d件 (id %d〜%d)' % (len(out), out[0]['newid'], out[-1]['newid']) if out else '投入0件')

json.dump(out, open('tmp/cand_0825.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump([{'artist': a, 'why': w, 'url': u} for a, w, u in loose],
          open('tmp/loose_0825.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('written tmp/cand_0825.json / tmp/loose_0825.json')
