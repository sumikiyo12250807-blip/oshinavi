# -*- coding: utf-8 -*-
"""10/1夕 7.5（ぴあ発売前一覧 10/2〜10/4）で抜けていた分を足す＝足し算（既存の枠は消さない）。
 足し込み4件（CANDY TUNE・呪術廻戦・万博花火・xikers）／新規16件（Plastic Tree 川崎12/27 は別公演なので新規）。
 新規は genre:new（_genre は build_pia_entries の判定）→ reconcile_pia --ids を通してから振り分ける。
使い方: python tmp/x1001/x/add/apply_add.py [--apply]"""
import datetime, io, json, re, sys
sys.path.insert(0, 'tools')
import heal_stale_deadlines as H
sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
D = 'tmp/x1001/x/add/'
MERGE = [4071, 6136, 7336, 9215]
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


def same(n, o):
    un, uo = H._url_id(n.get('url')), H._url_id(o.get('url'))
    return H.base_type(n.get('type')) == H.base_type(o.get('type')) and (un == uo or not n.get('url') or not o.get('url'))


lost_all, touched = 0, []
for bid in MERGE:
    e, b = by[bid], built[bid]
    lp = H._url_id((e.get('links') or {}).get('pia'))
    bp = (b.get('links') or {}).get('pia')
    old = e.get('tickets') or []
    new = []
    for t in b['tickets']:
        n = dict(t)
        if not n.get('url') and bp and H._url_id(bp) != lp:
            n['url'] = bp
        if not any(same(n, o) for o in old):
            new.append(n)
    e['tickets'] = old + new
    ko = {H.slot_key(t) for t in e['tickets']}
    lost_all += len([t for t in old if H.slot_key(t) not in ko])
    touched.append(bid)
    print('id%-5s %s ＋%d' % (bid, e['name'][:30], len(new)))
    for t in new:
        print('    ＋ %s | sd=%s d=%s url=%s' % (t.get('type'), t.get('startDate'), t.get('date'), t.get('url') or ''))
nid = max(by) + 1
added = []
order_ids = []
for bid in [3320] + list(range(90001, 90016)):
    b = built.get(bid)
    if not b:
        continue
    c = re.search(r'event(?:Bundle)?Cd=(\w+)', b['links']['pia']).group(1)
    if c in cds:
        print('!! 既に登録にある', c, b.get('artist')); continue
    if not b.get('tickets') or b.get('genre') != 'new':
        print('!! 枠0 or genre!=new', b.get('artist')); continue
    e = dict(b, id=nid)
    events.append(e)
    added.append(nid)
    print('新規 id%d %s ｜%s｜枠%d' % (nid, e['name'][:30], e.get('_genre'), len(e['tickets'])))
    nid += 1
print('\n消える枠 %d / 足し込み=%s / 新規=%s' % (lost_all, touched, added))
io.open(D + 'touched_ids.txt', 'w', encoding='utf-8').write(','.join(map(str, touched + added)))
io.open(D + 'new_ids.json', 'w').write(json.dumps(added))
if '--apply' not in sys.argv:
    sys.exit(0)
if lost_all:
    print('消える枠があるので書かない'); sys.exit(1)
body = '[\n' + ',\n'.join(json.dumps(x, ensure_ascii=False, separators=(',', ':')) for x in events) + '\n]'
text = src[:st] + body.replace('\n', '\r\n') + src[end:]
mo = re.search(r'NEW_ORDER\s*=\s*\[([^\]]*)\]', text)
ids = [x.strip() for x in mo.group(1).split(',') if x.strip()] + [str(i) for i in added]
text = text[:mo.start(1)] + ','.join(ids) + text[mo.end(1):]
io.open('index.html', 'wb').write(text.encode('utf-8'))
print('書き込み完了')
