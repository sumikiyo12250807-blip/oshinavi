# -*- coding: utf-8 -*-
"""新着のジャンルを、読み直しエージェントが保存したぴあの生HTMLのジャンル番号で確かめる（読むだけ・2026-09-16）。
compare_genre_0916.py で「判定できない」になった分（エージェントが大分類しか書かなかった分）を埋めるため。
番号は <input ... genreCd value="NNNNNNN"> か ntSgenreCd の7桁。名前は build_pia_entries.PIA_GENRE_CD で引く（推測しない）。
使い方: python tmp/genre_from_html_0916.py
"""
import glob
import io
import json
import os
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, 'tools')
from build_pia_entries import PIA_GENRE_CD  # noqa: E402

SP = r'C:\Users\user\AppData\Local\Temp\claude\C--Users-user-oshinavi\166bfbc5-2524-465f-aba5-b0b622c14861\scratchpad'
src = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
new = [e for e in ev if e.get('genre') == 'new']

files = {}
for p in glob.glob(os.path.join(SP, '**', '*.htm*'), recursive=True):
    if p.endswith('.url'):
        continue
    files.setdefault(os.path.basename(p).split('.')[0], p)


def n(s):
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', s or ''))


def codes_of(e):
    out = []
    for u in [(e.get('links') or {}).get('pia')] + [t.get('url') for t in e.get('tickets') or []]:
        m = re.search(r'event(?:Bundle)?Cd=(b?\d+)', u or '')
        if m and m.group(1) not in out:
            out.append(m.group(1))
    return out


GC = re.compile(r'(?:genreCd|ntSgenreCd)["\']?\s*(?:value=|[:=])\s*["\']?(\d{7})')
ok, bad, nohtml, nocode = [], [], [], []
for e in sorted(new, key=lambda x: x['id']):
    leaf = n((e.get('_piaSub') or '').split('/')[-1])
    got = set()
    seen = False
    for c in codes_of(e):
        p = files.get(c)
        if not p:
            continue
        seen = True
        h = io.open(p, encoding='utf-8', errors='replace').read()
        got |= {n(PIA_GENRE_CD.get(x, '?' + x)) for x in GC.findall(h)}
    if not seen:
        nohtml.append(e)
    elif not got:
        nocode.append(e)
    elif leaf in got:
        ok.append(e)
    else:
        bad.append((e, got))
print('一致 %d / 食い違い %d / 番号なし %d / 保存ページなし %d（新着 %d件）' % (len(ok), len(bad), len(nocode), len(nohtml), len(new)))
for e, got in bad:
    print('  ✗ id%d %s ／ 登録「%s」 ページ「%s」' % (e['id'], e['name'][:30], e.get('_piaSub'), '・'.join(sorted(got))))
for e in nocode[:10]:
    print('  ？番号なし id%d %s ／ 登録「%s」' % (e['id'], e['name'][:30], e.get('_piaSub')))
