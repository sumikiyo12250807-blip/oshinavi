# -*- coding: utf-8 -*-
"""9/28夜 presale_sweep.json の missing を eventCd でまとめ、今の index.html と再突合（tmp/x0928/split.py の夜版・読むだけ）。
出力: tmp/x0928e/w/cands.json（build入力）"""
import io, json, re, sys, unicodedata
sys.stdout.reconfigure(encoding='utf-8')
src = io.open('index.html', encoding='utf-8', newline='').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
MAXID = max(e['id'] for e in ev)
cd2ids = {}
for e in ev:
    blob = json.dumps(e.get('links') or {}, ensure_ascii=False) + ' ' + ' '.join(t.get('url') or '' for t in e.get('tickets') or [])
    for c in re.findall(r'event(?:Bundle)?Cd=(\w+)', blob):
        cd2ids.setdefault(c, set()).add(e['id'])
def nz(s):
    return unicodedata.normalize('NFKC', s or '').replace(' ', '').replace('　', '').lower()
d = json.load(open('tmp/x0928e/presale_sweep.json', encoding='utf-8'))
groups = {}
for r in d['missing']:
    cd = re.search(r'event(?:Bundle)?Cd=(\w+)', r['url']).group(1)
    groups.setdefault(cd, []).append(r)
cands = []
nid = MAXID + 1
for cd, rs in groups.items():
    if cd in cd2ids:
        print('既に登録', cd, rs[0]['artist'], sorted(cd2ids[cd])); continue
    a = nz(rs[0]['artist'])
    exact = [e['id'] for e in ev if nz(e.get('artist')) == a or nz(e.get('name')) == a]
    url = rs[0]['url'].replace('ticket.pia.jp/pia/event.do', 't.pia.jp/pia/event/event.do')
    cands.append({'newid': nid, 'artist': rs[0]['artist'], 'urls': [url], 'eventCd': cd, 'lg': rs[0]['_lg'], 'name_exact_ids': exact})
    print('%d %s | %s | %s | 名前完全一致=%s' % (nid, cd, rs[0]['_lg'], rs[0]['artist'], exact))
    for r in rs:
        print('      %s %s 公演%s %s' % (r['saletype'], r['rlsdate'], r['perfdate'], r['venue']))
    nid += 1
json.dump(cands, io.open('tmp/x0928e/w/cands.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('MAXID', MAXID, '候補', len(cands), '/ eventCd', len(groups), '/ 行', len(d['missing']))
