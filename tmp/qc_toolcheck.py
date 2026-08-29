# -*- coding: utf-8 -*-
import json, sys, io
sys.path.insert(0, r'C:\Users\user\oshinavi\tools')
import importlib.util
spec = importlib.util.spec_from_file_location('bpe', r'C:\Users\user\oshinavi\tools\build_pia_entries.py')
bpe = importlib.util.module_from_spec(spec); spec.loader.exec_module(bpe)
rows = json.load(open(r'C:\Users\user\oshinavi\tmp\qc_rows.json', encoding='utf-8'))
out=[]
for r in rows:
    cat, _, sub = r['sub'].partition('/')
    g = bpe.genre_from_subcat(cat, sub, (r['name'] or '') + ' ' + (r['artist'] or ''))
    tg = (r['theirs'], r['theirex'][0] if r['theirex'] else None)
    if g is None or g[0] != tg[0] or (g[1] or None) != (tg[1] or None):
        out.append(f"id={r['id']} sub={r['sub']} 保存={tg} ツール再計算={g} name={r['name']}")
open(r'C:\Users\user\oshinavi\tmp\qc_tool.txt','w',encoding='utf-8').write(
  f'ツール genre_from_subcat 再計算との差 {len(out)}件\n' + '\n'.join(out))
# 潜在の罠: 未使用サブでの分岐
probe = ['クラシック邦楽','フェスティバル・ガラコンサート','オーケストラ','器楽・室内楽','オペラ・声楽','吹奏楽','合唱','クラシックその他','eスポーツ','格闘技','球技その他']
p=[]
for s in probe:
    p.append(f"{s} -> {bpe.genre_from_subcat('クラシック' if s in ('クラシック邦楽','フェスティバル・ガラコンサート','オーケストラ','器楽・室内楽','オペラ・声楽','吹奏楽','合唱','クラシックその他') else 'スポーツ', s, 'テスト公演')}")
open(r'C:\Users\user\oshinavi\tmp\qc_probe.txt','w',encoding='utf-8').write('\n'.join(p))
print('ok')
