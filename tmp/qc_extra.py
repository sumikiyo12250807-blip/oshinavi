# -*- coding: utf-8 -*-
import json, re, collections, importlib.util
spec = importlib.util.spec_from_file_location('bpe', r'C:\Users\user\oshinavi\tools\build_pia_entries.py')
bpe = importlib.util.module_from_spec(spec); spec.loader.exec_module(bpe)
out=[]; w=out.append
w('=== 66サブカテゴリ全部を通した挙動（潜在の穴の洗い出し） ===')
lg2cat = bpe.PIA_LG_LABEL
for cd, sub in bpe.PIA_GENRE_CD.items():
    cat = lg2cat[cd[:2]]
    g = bpe.genre_from_subcat(cat, sub, 'テスト公演')
    exact = 'MAP' if sub in bpe.PIA_GENRE_MAP else ('分岐' if ('邦楽' in sub or '花火' in sub) else 'あいまい/CATfallback')
    w(f'{cat}/{sub}\t-> {g}\t[{exact}]')
w('')
w('=== 新着261件の重複チェック ===')
new = json.load(open(r'C:\Users\user\oshinavi\tmp\qc_new.json', encoding='utf-8'))
byname = collections.Counter((e.get('artist') or '') + '|' + (e.get('name') or '') for e in new)
for k,v in byname.items():
    if v>1: w(f'同名 {v}件: {k}')
ev = collections.Counter()
for e in new:
    u = (e.get('links') or {}).get('pia') or ''
    m = re.search(r'eventCd=(\d+)', u)
    if m: ev[m.group(1)] += 1
for k,v in ev.items():
    if v>1:
        ids=[e['id'] for e in new if f'eventCd={k}' in ((e.get('links') or {}).get('pia') or '')]
        w(f'同一eventCd {k} が {v}件: id={ids}')
w('')
w('=== NEW_ORDER と新着プールの照合 ===')
src = open(r'C:\Users\user\oshinavi\index.html', encoding='utf-8', newline='').read()
m2 = re.search(r'(const NEW_ORDER = )(\[[^\]]*\])', src)
order = json.loads(m2.group(2))
ids = {e['id'] for e in new}
w(f'NEW_ORDER {len(order)}件 / 新着プール {len(ids)}件')
w(f'NEW_ORDERにあるがプールに無い: {sorted(set(order)-ids)}')
w(f'プールにあるがNEW_ORDERに無い: {sorted(ids-set(order))}')
w(f'NEW_ORDER内の重複: {[k for k,v in collections.Counter(order).items() if v>1]}')
w('')
w('=== id連番の欠番（5332-5594） ===')
w(f'欠番: {sorted(set(range(5332,5595))-ids)}')
w('')
w('=== _extraGenres が空配列のまま残っている件数 ===')
w(f'{sum(1 for e in new if e.get("_extraGenres") == [])}件（空配列。assign時は falsy なので extraGenres は付かない＝害なし）')
open(r'C:\Users\user\oshinavi\tmp\qc_extra.txt','w',encoding='utf-8').write('\n'.join(out))
print('ok')
