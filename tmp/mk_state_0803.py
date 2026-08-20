# -*- coding: utf-8 -*-
"""tmp/kw_audit_0803.py で引いた結果を pia_missing_audit の状態ファイル形式に落とす。
grow_from_audit.py がそのまま読める（--state で渡す）。
own_name 判定は pia_missing_audit.same_name を再利用（自前判定を作らない）。
"""
import re, io, json, sys, os, time, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def load(name, fname):
    s = importlib.util.spec_from_file_location(name, os.path.join('tools', fname))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m

kw = load('kw', 'pia_kw_search.py')
pma = load('pma', 'pia_missing_audit.py')

h = io.open('index.html', encoding='utf-8', newline='').read()
EVENTS = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
CD = re.compile(r'event(?:Bundle)?Cd=(\w+)')
reg = set()
for e in EVENTS:
    reg.update(CD.findall((e.get('links') or {}).get('pia') or ''))
    for t in e.get('tickets') or []:
        reg.update(CD.findall(t.get('url') or ''))
excl = pma.load_excluded()

KWS = sys.argv[1:] or ['プロレスリング・ノア']
results = {}
for k in KWS:
    found = kw.search(k)
    miss = []
    for u, x in found.items():
        c = CD.findall(u)
        if not c or c[0] in reg or c[0] in excl:
            continue
        miss.append({'code': c[0], 'url': u, 'title': x['title'], 'status': x['status'],
                     'perfdate': x['perfdate'], 'venue': x['venue'], 'rlsdate': x['rlsdate'],
                     'own_name': pma.same_name(k, x['title'])})
    results[k] = {'hits': len(found), 'missing': miss}
    print('%s hits=%d missing=%d own=%d' % (k, len(found), len(miss),
                                            sum(1 for m in miss if m['own_name'])))
    time.sleep(3)

json.dump({'results': results}, io.open('tmp/kw_state_0803.json', 'w', encoding='utf-8'),
          ensure_ascii=False)
print('→ tmp/kw_state_0803.json')
