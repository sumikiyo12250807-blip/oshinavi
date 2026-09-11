# -*- coding: utf-8 -*-
"""前夜分の新着について、下書き _genre が「ぴあの区分(_piaSub)を対応表に通した答え」と一致するかを見る（読むだけ）。
対応表＝tools/build_pia_entries.genre_from_subcat（投入時と同じもの）。
一致しないもの＝投入時に手で直した（kpop読み替え等）か、ズレ＝要確認。
使い方: python tmp/genre_draft_check_0912.py
"""
import json
import re
import sys

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
from build_pia_entries import genre_from_subcat

LO, HI = 7840, 8157
s = open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);\s*\n', s, re.S).group(1))
ok, bad, nosub = 0, [], []
for e in ev:
    if e.get('genre') != 'new' or not (LO <= e['id'] <= HI):
        continue
    sub = e.get('_piaSub')
    if not sub:
        nosub.append(e['id'])
        continue
    parts = sub.split('/')
    lg, sc = (parts[0], parts[-1]) if len(parts) > 1 else ('', parts[0])
    want, extra = genre_from_subcat(lg, sc, e.get('artist', ''))
    if want == e.get('_genre'):
        ok += 1
    else:
        bad.append((e['id'], (e.get('artist') or '')[:30], sub, e.get('_genre'), want))
print('対応表どおり %d件 / ズレ %d件 / _piaSub無し %d件 %s' % (ok, len(bad), len(nosub), nosub))
for b in bad:
    print('  id%-5s %-30s ぴあ[%s] 下書き[%s] 対応表[%s]' % b)
