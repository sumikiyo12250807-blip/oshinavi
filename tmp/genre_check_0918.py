# -*- coding: utf-8 -*-
# 新着プールの _piaSub → 対応表 と _genre の突き合わせ（2026-08-31 のズレを機械で拾う）
import re, json, io, sys, importlib.util

spec = importlib.util.spec_from_file_location('bpe', 'tools/build_pia_entries.py')
bpe = importlib.util.module_from_spec(spec)
sys.modules['bpe'] = bpe
spec.loader.exec_module(bpe)
MAP = bpe.PIA_GENRE_MAP

src = open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'const EVENTS = (\[.*?\]);\n', src, re.S).group(1))
new = [e for e in ev if e.get('genre') == 'new']

out = io.open('tmp/genre_check_0918.txt', 'w', encoding='utf-8')
ok = mismatch = nosub = 0
for e in sorted(new, key=lambda x: x['id']):
    sub = e.get('_piaSub') or ''
    g = e.get('_genre')
    leaf = sub.split('/')[-1] if sub else ''
    exp = MAP.get(leaf)
    exp_g = exp[0] if isinstance(exp, tuple) else exp
    if not leaf or exp_g is None:
        nosub += 1
        out.write(f"❓ id{e['id']}\tsub={sub!r}\t_genre={g}\t対応表に無い\t{e.get('artist','')[:34]}\n")
    elif exp_g != g:
        mismatch += 1
        out.write(f"🚨 id{e['id']}\tsub={sub!r}\t_genre={g}\t対応表では {exp_g}\t{e.get('artist','')[:34]}\n")
    else:
        ok += 1
out.write(f"\n=== 一致 {ok} / 🚨ズレ {mismatch} / ❓対応表に無い {nosub}（全{len(new)}件）===\n")
out.close()
print(f"ok={ok} mismatch={mismatch} nosub={nosub} total={len(new)}")
