# -*- coding: utf-8 -*-
"""【投入前ゲート・緩い版】built した候補が既存エントリの「中に埋まっている」型を拾う。
2026-08-21夜に、dupcheck_built（正規化後の完全一致）が
「アンジュルム 2026秋 風林火山・弐」型（公演名にアーティスト名が含まれる）を見逃した。
判定＝片方の正規化名がもう片方に含まれる（4文字以上）。機械では決めきれないので候補を出すだけ。
使い方: python tmp/dupcheck_loose_built_0823.py tmp/built_0823.json
"""
import re, json, sys, io, unicodedata
sys.stdout.reconfigure(encoding='utf-8')

SRC = sys.argv[1] if len(sys.argv) > 1 else 'tmp/built_0823.json'
built = json.load(io.open(SRC, encoding='utf-8'))
h = io.open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))


def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　・\-–—~〜"\'`()（）【】「」『』\[\]!！?？。、,.:：/／★☆]', '', s).lower()


old = []
for e in EVENTS:
    for f in ('artist', 'name'):
        v = norm(e.get(f))
        if len(v) >= 4:
            old.append((v, e))

hits = []
for b in built:
    cands = set()
    for f in ('artist', 'name'):
        nb = norm(b.get(f))
        if len(nb) < 4:
            continue
        for ov, e in old:
            if e.get('genre') == 'new':
                continue
            if nb in ov or ov in nb:
                cands.add((e['id'], e.get('artist', ''), e.get('name', ''), e.get('date', '')))
    if cands:
        hits.append((b, sorted(cands)))

o = io.open('tmp/dupcheck_loose_built_0823.txt', 'w', encoding='utf-8')
o.write('=== 候補 %d件 / 部分一致で既存とぶつかった %d件 ===\n\n' % (len(built), len(hits)))
for b, cands in hits:
    o.write('■ 新 id%s %s | %s | %s\n' % (b['id'], b.get('artist'), b.get('name'), b.get('date')))
    for c in cands:
        o.write('    ↔ 既存 id%s %s | %s | %s\n' % c)
    o.write('\n')
o.close()
print('候補 %d件 / 部分一致 %d件 → tmp/dupcheck_loose_built_0823.txt' % (len(built), len(hits)))
