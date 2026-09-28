# -*- coding: utf-8 -*-
"""7.5（9/28夜）：ぴあが後から足した枠を既存エントリへ「足し算」で入れる。
・組み立て（tmp/x0928/x/built.json）の枠のうち、登録に同じ枠（券種の基底名が同じ・飛び先が同じか空）が無いものだけ足す
・登録の枠は1枚も外さない
・22538 は 12/15公演が増えたので date / dateLabel を組み立ての会期に合わせる（事実の会期）
使い方: python tmp/x0928/x/add_windows.py [--apply]
"""
import datetime, io, json, re, shutil, sys
sys.path.insert(0, 'tools')
import heal_stale_deadlines as H
sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
IDS = [24379, 22538, 3252]
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
by = {e['id']: e for e in events}
built = {e['id']: e for e in json.load(io.open('tmp/x0928/x/built.json', encoding='utf-8'))}


def same(n, o):
    un, uo = H._url_id(n.get('url')), H._url_id(o.get('url'))
    return H.base_type(n.get('type')) == H.base_type(o.get('type')) and (un == uo or not n.get('url') or not o.get('url'))


added = []
for i in IDS:
    e, b = by[i], built[i]
    old = e.get('tickets') or []
    vis0 = sum(1 for t in old if H.visible_slot(t, TODAY))
    new = [dict(t) for t in b['tickets'] if not any(same(t, o) for o in old)]
    e['tickets'] = old + new
    if i == 22538:
        e['date'], e['dateLabel'] = b['date'], b['dateLabel']
    vis1 = sum(1 for t in e['tickets'] if H.visible_slot(t, TODAY))
    print('id%s %s ｜出る枠 %d→%d ＋%d' % (i, e['name'], vis0, vis1, len(new)))
    for t in new:
        print('    ＋ %s | sd=%s d=%s' % (t.get('type'), t.get('startDate'), t.get('date')))
    added.append((i, len(new)))
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
shutil.copyfile('index.html', 'tmp/x0928/x/index_before_75.html')
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('書き込み完了', added)
