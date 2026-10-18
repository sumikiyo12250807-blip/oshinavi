# -*- coding: utf-8 -*-
"""2026-10-18 すちこ「A」＝県名を短い形にそろえる（東京都→東京・大阪府→大阪…）。
直す所＝prefecture の欄／券種名の「（東京都 12/19公演）」の県の部分／dateLabel の県の語（空白で区切られた語だけ）。
会場名（「東京都庭園美術館」など）は触らない。
  python tmp/x1018/short_pref_migrate.py          … 下見
  python tmp/x1018/short_pref_migrate.py --apply
"""
import io, json, os, re, sys
os.chdir(r'C:\Users\user\oshinavi')
sys.path.insert(0, 'tools')
import eplus_harvest as E
sys.stdout = io.TextIOWrapper(open(1, 'wb', closefd=False), encoding='utf-8', line_buffering=True)
LONG = E._PREF_LONG
ALL = set(LONG) | set(LONG.values()) | {'北海道'}


def fix_group(g):
    toks = g.split('・')
    if all(t in ALL for t in toks) and any(t in LONG for t in toks):
        return '・'.join(LONG.get(t, t) for t in toks)
    return None


src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
n_pref = n_type = n_label = 0
ex = []
for e in events:
    p = e.get('prefecture') or ''
    np = fix_group(p) if p else None
    if np:
        e['prefecture'] = np
        n_pref += 1
        if len(ex) < 5:
            ex.append((e['id'], p, np))
    dl = e.get('dateLabel') or ''
    parts = dl.split(' ')
    nparts = [fix_group(x) or x for x in parts]
    if nparts != parts:
        e['dateLabel'] = ' '.join(nparts)
        n_label += 1
    for t in e.get('tickets') or []:
        ty = t.get('type') or ''
        nt = re.sub(r'（([^（）\s]+) ', lambda mm: '（' + (fix_group(mm.group(1)) or mm.group(1)) + ' ', ty)
        if nt != ty:
            t['type'] = nt
            n_type += 1
print('県の欄', n_pref, '／dateLabel', n_label, '／券種名', n_type)
print('例', ex)
left = sum(1 for e in events if re.search(r'(東京都|大阪府|神奈川県|愛知県)', e.get('prefecture') or ''))
print('県の欄に長い形が残った', left)
if '--apply' in sys.argv:
    nl = '\r\n' if '\r\n' in src else '\n'
    out = (src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl)
           + m.group(3) + src[m.end():])
    io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
    print('書いた')
