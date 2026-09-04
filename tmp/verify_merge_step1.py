# -*- coding: utf-8 -*-
"""index.html を読み取り専用でパースして、同名エントリ組を洗い出す"""
import re, json, unicodedata, sys, io, collections, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PATH = r'C:\Users\user\oshinavi\index.html'
TODAY = '2026-09-04'
OUT = r'C:\Users\user\oshinavi\tmp'

src = open(PATH, encoding='utf-8', newline='').read()
m = re.search(r'const EVENTS = (\[.*?\]);', src, re.S)
if not m:
    print('EVENTS not found'); sys.exit(1)
EVENTS = json.loads(m.group(1))
print('total entries:', len(EVENTS))

# id ユニーク確認
ids = [e.get('id') for e in EVENTS]
print('unique ids:', len(set(ids)))

def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    s = s.lower()
    # 記号・空白を全部落とす（英数字＋日本語文字だけ残す）
    s = re.sub(r'[^0-9a-z\u3040-\u30ff\u4e00-\u9fff\uff66-\uff9f]', '', s)
    return s

groups = collections.defaultdict(list)
for e in EVENTS:
    groups[norm(e.get('name',''))].append(e)

dupgroups = {k:v for k,v in groups.items() if len(v) >= 2 and k}
print('name-collision groups (>=2):', len(dupgroups))
print('entries involved:', sum(len(v) for v in dupgroups.values()))

sizes = collections.Counter(len(v) for v in dupgroups.values())
print('group size distribution:', dict(sorted(sizes.items())))

def visible(t):
    if t.get('saleUntilSoldOut') or t.get('soldout'): return True
    sd, d = t.get('startDate'), (t.get('date') or '')
    return not ((not sd or sd <= TODAY) and d < TODAY)

# --- エントリをまたいだ重複枠 (type,date,url) ---
slotmap = collections.defaultdict(list)
for e in EVENTS:
    for t in (e.get('tickets') or []):
        key = (t.get('type'), t.get('date'), t.get('url'))
        slotmap[key].append(e.get('id'))

cross = {k:v for k,v in slotmap.items() if len(set(v)) >= 2}
print('cross-entry duplicate slot keys:', len(cross))
print('cross-entry duplicate slot rows:', sum(len(v) for v in cross.values()))
# 同名グループ内に限った重複
name_of = {e.get('id'): norm(e.get('name','')) for e in EVENTS}
cross_samename = {k:v for k,v in cross.items() if len(set(name_of[i] for i in set(v)))==1}
print('  of which within same-name group:', len(cross_samename))
# visible な重複だけ
vis_slotmap = collections.defaultdict(list)
for e in EVENTS:
    for t in (e.get('tickets') or []):
        if visible(t):
            vis_slotmap[(t.get('type'), t.get('date'), t.get('url'))].append(e.get('id'))
cross_vis = {k:v for k,v in vis_slotmap.items() if len(set(v))>=2}
print('cross-entry duplicate VISIBLE slot keys:', len(cross_vis))
print('cross-entry duplicate VISIBLE slot rows:', sum(len(v) for v in cross_vis.values()))

# --- グループ詳細をファイルに ---
def dump(f, g):
    for e in sorted(g, key=lambda x: x.get('id')):
        ts = e.get('tickets') or []
        vs = [t for t in ts if visible(t)]
        f.write('  id=%s | name=%s\n' % (e.get('id'), e.get('name')))
        f.write('    genre=%s area=%s venue=%s date=%s\n' % (e.get('genre'), e.get('area'), e.get('venue'), e.get('date')))
        f.write('    subtitle/desc=%s\n' % (str(e.get('description') or e.get('subtitle') or '')[:160],))
        f.write('    tickets=%d visible=%d\n' % (len(ts), len(vs)))
        for t in ts:
            f.write('      %s[%s] type=%s start=%s end=%s sold=%s url=%s\n' % (
                'V' if visible(t) else '.', t.get('dateLabel',''), t.get('type'),
                t.get('startDate'), t.get('date'), t.get('soldout'), (t.get('url') or '')[:110]))

with open(os.path.join(OUT,'groups_full.txt'),'w',encoding='utf-8') as f:
    for k,g in sorted(dupgroups.items(), key=lambda kv:(-len(kv[1]), kv[0])):
        f.write('=== %s  (n=%d) ===\n' % (g[0].get('name'), len(g)))
        dump(f,g)
        f.write('\n')

# サマリ表（1行1グループ）
with open(os.path.join(OUT,'groups_summary.tsv'),'w',encoding='utf-8') as f:
    f.write('n\tname\tids\tgenres\tvenues\tdates\tvisible_counts\n')
    for k,g in sorted(dupgroups.items(), key=lambda kv:(-len(kv[1]), kv[0])):
        f.write('%d\t%s\t%s\t%s\t%s\t%s\t%s\n' % (
            len(g), g[0].get('name'),
            ','.join(str(e.get('id')) for e in g),
            '|'.join(sorted(set(str(e.get('genre')) for e in g))),
            '|'.join(str(e.get('venue')) for e in g),
            '|'.join(str(e.get('date')) for e in g),
            ','.join(str(len([t for t in (e.get('tickets') or []) if visible(t)])) for e in g)))
print('written: tmp/groups_full.txt, tmp/groups_summary.tsv')
