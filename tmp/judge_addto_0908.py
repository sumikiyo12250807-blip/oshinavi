# -*- coding: utf-8 -*-
"""候補27件と既存エントリのticketsを並べてUTF-8ファイルに書き出す。"""
import json, re, io, sys

ROOT = r'C:\Users\user\oshinavi'
h = open(ROOT + r'\index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
assert m, 'EVENTS not found'
EVENTS = json.loads(m.group(2))
BY = {e['id']: e for e in EVENTS}

cands = json.load(open(ROOT + r'\tmp\inject_addto_0908.json', encoding='utf-8'))

# dedup_0908.md の「⚠️」節から 候補id -> 既存id群 を読む
md = open(ROOT + r'\tmp\dedup_0908.md', encoding='utf-8').read()
sec = md.split('## ⚠️ 名前は同じだが既存に無い窓がある')[1]
pairs = {}
cur = None
for line in sec.splitlines():
    m1 = re.match(r'- id(\d+) ', line)
    if m1:
        cur = int(m1.group(1)); pairs[cur] = []
        continue
    m2 = re.search(r'⇔ 既存 id=(\d+)', line)
    if m2 and cur:
        pairs[cur].append(int(m2.group(1)))

out = io.StringIO()
for c in cands:
    cid = c['id']
    out.write('=' * 78 + '\n')
    out.write('候補 id%d  %s\n' % (cid, c.get('name')))
    out.write('  artist=%s  genre=%s/%s\n' % (c.get('artist'), c.get('genre'), c.get('_genre')))
    out.write('  会場=%s  県=%s  公演日=%s\n' % (c.get('venue'), c.get('prefecture'), c.get('date')))
    out.write('  dateLabel=%s\n' % c.get('dateLabel'))
    out.write('  pia=%s\n' % (c.get('links', {}) or {}).get('pia'))
    out.write('  tickets(%d):\n' % len(c.get('tickets') or []))
    for t in c.get('tickets') or []:
        out.write('    - type=%s | date=%s | startDate=%s | url=%s\n' % (
            t.get('type'), t.get('date'), t.get('startDate'), t.get('url')))
    for eid in pairs.get(cid, []):
        e = BY.get(eid)
        if not e:
            out.write('  --- 既存 id%d : index.htmlに無い\n' % eid)
            continue
        out.write('  --- 既存 id%d  %s\n' % (eid, e.get('name')))
        out.write('      artist=%s  genre=%s  会場=%s  県=%s  公演日=%s\n' % (
            e.get('artist'), e.get('genre'), e.get('venue'), e.get('prefecture'), e.get('date')))
        out.write('      dateLabel=%s\n' % e.get('dateLabel'))
        out.write('      pia=%s\n' % (e.get('links', {}) or {}).get('pia'))
        out.write('      tickets(%d):\n' % len(e.get('tickets') or []))
        for t in e.get('tickets') or []:
            out.write('        - type=%s | date=%s | startDate=%s | url=%s\n' % (
                t.get('type'), t.get('date'), t.get('startDate'), t.get('url')))
    out.write('\n')

open(ROOT + r'\tmp\judge_addto_0908.txt', 'w', encoding='utf-8').write(out.getvalue())
print('OK wrote tmp/judge_addto_0908.txt  cands=%d pairs=%d' % (len(cands), len(pairs)))
