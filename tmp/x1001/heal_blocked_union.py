# -*- coding: utf-8 -*-
"""10/1朝：安全弁で止まった45件に取り直しを「足し算」で当てる（tmp/heal_blocked_union_0930noon.py と同じ考え方）
  ・取り直しの枠は全部入れる／元の枠は置き換えられた分だけ外す／売り切れ印の元の枠は残す
使い方: python tmp/x1001/heal_blocked_union.py [--apply] → tmp/x1001/heal_blocked_union.txt
"""
import datetime, io, json, re, sys
sys.path.insert(0, 'C:/Users/user/oshinavi/tools')
import heal_stale_deadlines as H
root = 'C:/Users/user/oshinavi/'
TODAY = datetime.date.today().isoformat()
SRC = 'tmp/heal_stale.json'
if '--ids' in sys.argv:  # 使い方2: --ids 1,2 --src tmp/heal_ids.json
    ids = [int(x) for x in sys.argv[sys.argv.index('--ids') + 1].split(',')]
    SRC = sys.argv[sys.argv.index('--src') + 1]
else:
    LOG = sys.argv[sys.argv.index('--log') + 1] if '--log' in sys.argv else 'tmp/x1001/heal_apply.txt'
    log = io.open(root + LOG, encoding='utf-8').read()
    blk = log.split('🛡️', 1)[1]
    blk = re.split(r'\n\s*\n', blk, maxsplit=1)[0] if '\n\n' in blk else blk
    ids = [int(x) for x in re.findall(r'id=(\d+)', blk)]
out = io.open(root + 'tmp/x1001/heal_blocked_union.txt', 'w', encoding='utf-8')
out.write(f'止まった {len(ids)}件: {ids}\n')
text = io.open(root + 'index.html', encoding='utf-8', newline='').read()
mm = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
st = mm.start(1)
events, end = json.JSONDecoder().raw_decode(text, st)
by = {e['id']: e for e in events}
built = {o['id']: o for o in json.load(io.open(root + SRC, encoding='utf-8')) if o.get('status') == 'convert'}
OLD_FORM = re.compile(r'\d{1,2}/\d{1,2}\s*\d{1,2}:\d{2}\s*発売\s*$')


def replaces(n, o):
    bn, bo = H.base_type(n.get('type')), H.base_type(o.get('type'))
    un, uo = H._url_id(n.get('url')), H._url_id(o.get('url'))
    if bn == bo and (un == uo or not n.get('url') or not o.get('url') or OLD_FORM.search(o.get('type') or '')):
        return True
    strip = lambda s: re.sub(r'【[^】]*】', '', s)
    return bool(n.get('url') and o.get('url') and un == uo and '【' not in bo
                and strip(bn) == bo and H.perf_key(n.get('type')) == H.perf_key(o.get('type')))


def vis(ts):
    return sum(1 for t in ts if H.visible_slot(t, TODAY))


total, lostn = 0, 0
for i in ids:
    e, o = by.get(i), built.get(i)
    if not e or not o:
        out.write('id%-5s 取り直し無し＝触らない\n' % i); continue
    old = e.get('tickets') or []
    new = [dict(t) for t in o['tickets']]
    gone, kept = [], []
    for t in old:
        rep = [n for n in new if replaces(n, t)]
        if rep and not t.get('soldout'):
            for n in rep:
                if not n.get('url') and t.get('url'): n['url'] = t['url']
                if not n.get('startDate') and t.get('startDate'): n['startDate'] = t['startDate']
            gone.append(t)
        else:
            kept.append(t)
    merged = new + kept
    ko = {H.slot_key(t) for t in merged if H.visible_slot(t, TODAY)}
    lost = [t for t in old if H.visible_slot(t, TODAY) and H.slot_key(t) not in ko and not any(replaces(n, t) for n in new)]
    lostn += len(lost)
    e['tickets'] = merged
    total += 1
    out.write('id%-5s %s ｜出る枠 %d→%d（取り直し%d・置き換え%d・残す%d）%s\n' % (
        i, (e.get('name') or '')[:24], vis(old), vis(merged), len(new), len(gone), len(kept),
        '  🚨消える枠 %d' % len(lost) if lost else ''))
out.write(f'\n{total}件 / 消える枠 {lostn}\n')
if '--apply' in sys.argv:
    body = '[\n' + ',\n'.join(json.dumps(x, ensure_ascii=False, separators=(',', ':')) for x in events) + '\n]'
    text = text[:st] + body.replace('\n', '\r\n') + text[end:]
    io.open(root + 'index.html', 'wb').write(text.encode('utf-8'))
    out.write('書き込み完了\n')
