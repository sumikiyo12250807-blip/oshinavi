# -*- coding: utf-8 -*-
"""同一ツアーが別エントリに分かれてるのを統合。各クラスタの全ぴあURLを build() で
再導出→会場別url付き1エントリにマージ→最小idに格納・残idは削除・NEW_ORDER更新。
※This is LASTは別物(Zeppツアー2027 vs 武道館2026)なので対象外。"""
import re, json, importlib.util, shutil
spec = importlib.util.spec_from_file_location('bpe', 'tools/build_pia_entries.py')
bpe = importlib.util.module_from_spec(spec); spec.loader.exec_module(bpe)

# クラスタ: keep_id, [全id], 統合後アーティスト名
CLUSTERS = [
    (1500, [1500,1501,1502,1503,1504], 'TK from 凛として時雨 TOUR 2026 生癖 -seiheki-'),
    (1516, [1516,1517,1518], 'TOTALFAT'),
    (1519, [1519,1520], 'Doona'),
    (1534, [1534,1535], '栄喜'),
]

txt = open('index.html', encoding='utf-8').read()
m = re.search(r'const EVENTS = (\[.*?\]);', txt, re.S)
arr = json.loads(m.group(1)); byid = {e['id']: e for e in arr}

delete_ids = set()
for keep, ids, artist in CLUSTERS:
    urls = []
    for i in ids:
        u = (byid[i].get('links') or {}).get('pia')
        if u and u not in urls: urls.append(u)
    cand = {'newid': keep, 'artist': artist, 'urls': urls}
    merged = bpe.build(cand)
    if not merged:
        print(f"!! {artist} build失敗(売切?) skip"); continue
    merged['genre'] = 'new'   # プールのまま(振り分けはユーザー後)
    # keep_idエントリを置換
    old = byid[keep]
    old.clear(); old.update(merged); old['id'] = keep
    delete_ids.update(set(ids) - {keep})
    print(f"統合 {artist[:26]}: id{ids} → id{keep} ({len(merged['tickets'])}枠 venue={merged['venue'][:30]})")

# 削除
arr = [e for e in arr if e['id'] not in delete_ids]

new_block = json.dumps(arr, ensure_ascii=False, indent=2)
new_txt = txt[:m.start(1)] + new_block + txt[m.end(1):]

# NEW_ORDER更新(残った1494-1543)
remain = sorted(e['id'] for e in arr if 1494 <= e['id'] <= 1543)
no_new = '[' + ', '.join(str(i) for i in remain) + ']'
new_txt, n = re.subn(r'(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]', r'\g<1>' + no_new, new_txt, count=1)
assert n == 1
json.loads(re.search(r'const EVENTS = (\[.*?\]);', new_txt, re.S).group(1))
shutil.copy('index.html', 'index.html.bak_0628_merge')
open('index.html', 'w', encoding='utf-8').write(new_txt)
print(f"\n削除 {sorted(delete_ids)} / 新着プール {len(remain)}件 / NEW_ORDER更新")
print("backup: index.html.bak_0628_merge")
