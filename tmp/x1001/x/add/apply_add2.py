# -*- coding: utf-8 -*-
"""8 取りこぼし総ざらいの分を足す＝足し算。ハク。3公演→26850／純烈 関内・相模原→2405／新規＝空気階段 配信・花江夏樹 2/28神奈川。
使い方: python tmp/x1001/x/add/apply_add2.py [--apply]"""
import io, json, re, sys
sys.path.insert(0, 'tools')
import heal_stale_deadlines as H
sys.stdout.reconfigure(encoding='utf-8')
D = 'tmp/x1001/x/add/'
MAP = {91001: 26850, 91002: 26850, 91003: 26850, 91006: 2405}
NEW = [91005, 91007]
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[)', src)
st = m.start(1)
events, end = json.JSONDecoder().raw_decode(src, st)
by = {e['id']: e for e in events}
built = {e['id']: e for e in json.load(io.open(D + 'built.json', encoding='utf-8'))}
cds = set()
for e in events:
    for u in [(e.get('links') or {}).get('pia') or ''] + [t.get('url') or '' for t in e.get('tickets') or []]:
        cds.update(re.findall(r'event(?:Bundle)?Cd=(\w+)', u))
for bid, tid in MAP.items():
    b, e = built[bid], by[tid]
    bp = b['links']['pia']
    c = re.search(r'event(?:Bundle)?Cd=(\w+)', bp).group(1)
    if c in cds:
        print('!! 既に登録にある', c); continue
    for t in b['tickets']:
        n = dict(t)
        n.setdefault('url', bp)
        if not n.get('url'):
            n['url'] = bp
        e['tickets'].append(n)
        print('id%d %s ＋ %s | %s' % (tid, e['name'][:20], n['type'], n['url']))
added = []
nid = max(by) + 1
for bid in NEW:
    b = built[bid]
    c = re.search(r'event(?:Bundle)?Cd=(\w+)', b['links']['pia']).group(1)
    if c in cds or not b.get('tickets') or b.get('genre') != 'new':
        print('!! 外す', b.get('artist')); continue
    events.append(dict(b, id=nid)); added.append(nid)
    print('新規 id%d %s ｜%s' % (nid, b['name'][:30], b.get('_genre')))
    nid += 1
io.open(D + 'new_ids2.json', 'w').write(json.dumps(added))
if '--apply' not in sys.argv:
    sys.exit(0)
body = '[\n' + ',\n'.join(json.dumps(x, ensure_ascii=False, separators=(',', ':')) for x in events) + '\n]'
text = src[:st] + body.replace('\n', '\r\n') + src[end:]
mo = re.search(r'NEW_ORDER\s*=\s*\[([^\]]*)\]', text)
ids = [x.strip() for x in mo.group(1).split(',') if x.strip()] + [str(i) for i in added]
text = text[:mo.start(1)] + ','.join(ids) + text[mo.end(1):]
io.open('index.html', 'wb').write(text.encode('utf-8'))
print('書き込み完了')
