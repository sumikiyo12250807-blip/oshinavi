# -*- coding: utf-8 -*-
"""投入前の重複チェック＝同じ公演日×会場（正規化）が既存DBにいないか。"""
import json, io, re, unicodedata

def nz(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　・･]', '', s).lower()

hh = io.open('index.html', encoding='utf-8').read()
db = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);', hh, re.S).group(1))
built = json.load(io.open('tmp/eplus_built.json', encoding='utf-8'))

# 既存の (日付, 会場正規化) と (日付, アーティスト正規化)
idx_v, idx_a = {}, {}
for e in db:
    dates = set()
    if e.get('date'):
        dates.add(e['date'])
    for t in (e.get('tickets') or []):
        for m in re.finditer(r'(\d{1,2})/(\d{1,2})公演', t.get('type') or ''):
            dates.add('%02d-%02d' % (int(m.group(1)), int(m.group(2))))
    for v in re.split(r'[／/]', re.sub(r'^全国ツアー（|）$', '', e.get('venue') or '')):
        if nz(v):
            for d in dates:
                idx_v.setdefault((d[-5:], nz(v)), []).append(e['id'])
    if nz(e.get('artist')):
        for d in dates:
            idx_a.setdefault((d[-5:], nz(e.get('artist'))), []).append(e['id'])

out = io.open('tmp/dupcheck_built_0905.txt', 'w', encoding='utf-8')
hits = 0
for b in built:
    dates = set()
    for t in b.get('tickets', []):
        for m in re.finditer(r'(\d{1,2})/(\d{1,2})公演', t.get('type') or ''):
            dates.add('%02d-%02d' % (int(m.group(1)), int(m.group(2))))
    if not dates and b.get('date'):
        dates.add(b['date'][-5:])
    vs = [v for v in re.split(r'[／/]', re.sub(r'^全国ツアー（|）$', '', b.get('venue') or '')) if nz(v)]
    found = set()
    for d in dates:
        for v in vs:
            for i in idx_v.get((d, nz(v)), []):
                found.add(('会場一致', d, v, i))
        for i in idx_a.get((d, nz(b.get('artist'))), []):
            found.add(('名前一致', d, b.get('artist'), i))
    if found:
        hits += 1
        out.write('■ id%s %s\n' % (b['id'], b['name']))
        for f in sorted(found):
            out.write('    %s %s %s → 既存id%s\n' % f)
out.write('\n疑い %d件 / 全%d件\n' % (hits, len(built)))
out.close()
print('DUP_SUSPECT=%d / %d' % (hits, len(built)))
