# -*- coding: utf-8 -*-
"""reconcile の結果から MISSING が出たエントリのidと、そのぴあURLを取り出す。"""
import io, re, json, sys, collections
sys.stdout.reconfigure(encoding='utf-8')

txt = io.open('tmp/reconcile_zero_0909.txt', encoding='utf-8').read()
cur = None
miss = collections.OrderedDict()
for line in txt.splitlines():
    m = re.match(r'^🚨 id=(\d+) (.*?) \|', line)
    if m:
        cur = int(m.group(1))
        miss.setdefault(cur, {'name': m.group(2).strip(), 'slots': []})
        continue
    m = re.match(r'^\s+🚨MISSING (.*)$', line)
    if m and cur:
        miss[cur]['slots'].append(m.group(1))

h = io.open('index.html', encoding='utf-8', newline='').read()
by = {e['id']: e for e in json.loads(re.search(r'const EVENTS = (\[.*?\]);\r?\n', h, re.S).group(1))}

print('MISSINGが出たエントリ %d件 / 枠 %d' % (len(miss), sum(len(v['slots']) for v in miss.values())))
rows = []
for i, v in miss.items():
    pia = (by.get(i, {}).get('links') or {}).get('pia') or ''
    cd = re.search(r'event(?:Bundle)?Cd=([\w\d]+)', pia)
    rows.append({'id': i, 'name': v['name'], 'pia': pia, 'cd': cd.group(1) if cd else '', 'n': len(v['slots'])})
    print('  id%-6d %-34s 枠%d  %s' % (i, v['name'][:34], len(v['slots']), pia))
json.dump(rows, io.open('tmp/missing_rows_0909.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
