# -*- coding: utf-8 -*-
"""別会場の公演を足したエントリの会場名に、足した会場を加える（2026-09-11）。
merge_with_urls は会場を作り直さない（駐車券などの会場を混ぜないため）ので、
**公演の会場だと確かめた分だけ**ここで足す。
使い方: python tmp/fix_venue_merged_0911.py <built.json> <元id>:<先id>,...
"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
built = {e['id']: e for e in json.load(io.open(sys.argv[1], encoding='utf-8-sig'))}
pairs = [tuple(map(int, p.split(':'))) for p in sys.argv[2].split(',')]
src = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
ev = json.loads(m.group(2))
by = {e['id']: e for e in ev}
for s, d in pairs:
    e, b = by[d], built[s]
    v = e.get('venue') or ''
    inner = re.match(r'^全国ツアー（(.*)）$', v)
    names = inner.group(1).split('／') if inner else [v]
    bv = b.get('venue') or ''
    bi = re.match(r'^全国ツアー（(.*)）$', bv)
    for n in (bi.group(1).split('／') if bi else [bv]):
        if n and n not in names:
            names.append(n)
    new = '全国ツアー（%s）' % '／'.join(names) if len(names) > 1 else names[0]
    if new != v:
        print('id%s %s → %s' % (d, v, new))
        e['venue'] = new
open('index.html', 'w', encoding='utf-8').write(src[:m.start()] + m.group(1) + json.dumps(ev, ensure_ascii=False, indent=2) + m.group(3) + src[m.end():])
