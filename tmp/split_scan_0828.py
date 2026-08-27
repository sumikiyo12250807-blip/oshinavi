# -*- coding: utf-8 -*-
"""同じアーティスト/興行が複数エントリに割れていないかをローカルで洗う（ネット不使用）。
スポーツのホーム/アウェイは畳んではダメなので除外して数える。"""
import re, io, json, collections, sys
sys.stdout.reconfigure(encoding='utf-8')
h = io.open('index.html', encoding='utf-8').read()
E = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))

def norm(s):
    s = (s or '')
    s = re.sub(r'[\s　]+', '', s)
    s = re.sub(r'[【】\[\]（）\(\)『』「」〜~・,，、。!！?？:：/／|｜]', '', s)
    return s.lower()

SKIP = ('sports',)
by = collections.defaultdict(list)
for e in E:
    if e.get('genre') in SKIP:
        continue
    a = norm(e.get('artist') or e.get('name'))
    if not a or len(a) < 3:
        continue
    by[a].append(e)

rows = []
for a, es in by.items():
    if len(es) < 2:
        continue
    # 生きた枠（未来の締切）を持つものだけ対象
    rows.append((a, es))

rows.sort(key=lambda kv: -len(kv[1]))
o = io.open('tmp/split_scan_0828.txt', 'w', encoding='utf-8')
o.write('=== 同名アーティストで複数エントリ（スポーツ除く）%d組 ===\n' % len(rows))
for a, es in rows:
    o.write('■ %s  (%d件)\n' % (es[0].get('artist') or es[0].get('name'), len(es)))
    for e in es:
        n = len(e.get('tickets') or [])
        o.write('    id%-6s %s | %s | 枠%d | %s\n' % (
            e['id'], e.get('date'), (e.get('name') or '')[:46], n,
            ((e.get('links') or {}).get('pia') or (e.get('links') or {}).get('eplus') or '')[:70]))
o.close()
print('複数エントリ組:', len(rows))
print('→ tmp/split_scan_0828.txt')
