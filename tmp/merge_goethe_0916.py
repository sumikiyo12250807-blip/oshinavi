# -*- coding: utf-8 -*-
"""10439 goethe（愛知 11/29 だけ）を、ぴあで販売期間中の北海道 11/8・大阪 11/21・東京 12/4 を足したツアー1件に広げる（2026-09-16 朝）。
見つけ方＝新着の読み直しで 10439 のページが一時「見つかりませんでした」→ ぴあを名前で検索（tools/pia_kw_search.py goethe）→ 3公演が販売期間中。
組み立て＝tools/build_pia_entries.py に1公演ずつ渡した（複数URLを1本で渡すと2本目以降の飛び先が落ちる癖＝feedback_build_pia_multiurl_loses_ticket_url）。
各枠には組み立てた公演ページの飛び先を焼き込む。10439 の番号・新着のまま・下書きジャンルは据え置き。
使い方: python tmp/merge_goethe_0916.py [--apply]
"""
import datetime
import io
import json
import re
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')
P = 'index.html'
ID = 10439
WD = '月火水木金土日'
built = json.load(io.open('tmp/built_goethe_0916.json', encoding='utf-8'))
cands = {c['newid']: c for c in json.load(io.open('tmp/cands_goethe_0916.json', encoding='utf-8'))}
assert len(built) == 4, len(built)


def events(text):
    return json.loads(re.search(r'  const EVENTS = (\[.*?\]);', text, re.S).group(1))


def jp(d):
    x = datetime.date.fromisoformat(d)
    return '%d年%d月%d日(%s)' % (x.year, x.month, x.day, WD[x.weekday()])


with open(P, encoding='utf-8', newline='') as f:
    text = f.read()
ev = events(text)
old = next(e for e in ev if e['id'] == ID)

shows = []   # (公演日, 県, 会場)
tickets = []
for b in built:
    url = cands[b['id']]['urls'][0].replace('https://ticket.pia.jp/pia/event.do', 'https://t.pia.jp/pia/event/event.do')
    for t in b['tickets']:
        t2 = dict(t)
        t2.setdefault('url', url)
        tickets.append(t2)
    shows.append((b['date'], b['prefecture'], b['venue']))
shows.sort()
tickets.sort(key=lambda t: t.get('date') or '')
prefs = []
for _, p, _ in shows:
    if p not in prefs:
        prefs.append(p)
assert len(prefs) <= 4

new_e = json.loads(json.dumps(old, ensure_ascii=False))
new_e['tickets'] = tickets
new_e['date'] = shows[-1][0]
new_e['dateLabel'] = '%s〜%s %s' % (jp(shows[0][0]), jp(shows[-1][0]), '・'.join(prefs))
new_e['venue'] = '全国ツアー（%s）' % '／'.join(v for _, _, v in shows)
new_e['prefecture'] = '・'.join(prefs)
new_e['verifiedAt'] = '2026-09-16'
new_e = {k: new_e[k] for k in old.keys()}

block = ['  ' + ln for ln in json.dumps(new_e, ensure_ascii=False, indent=2).split('\n')]
lines = text.split('\r\n')
out, i, hit = [], 0, 0
while i < len(lines):
    if lines[i] == '  {' and i + 1 < len(lines) and lines[i + 1] == '    "id": %d,' % ID:
        j = i
        while not lines[j].startswith('  }'):
            j += 1
        block[-1] += lines[j][3:]
        out += block
        hit += 1
        i = j + 1
        continue
    out.append(lines[i])
    i += 1
assert hit == 1
res = '\r\n'.join(out)
ev2 = events(res)
a = {x['id']: json.dumps(x, ensure_ascii=False, sort_keys=True) for x in ev2 if x['id'] != ID}
b2 = {x['id']: json.dumps(x, ensure_ascii=False, sort_keys=True) for x in ev if x['id'] != ID}
assert a == b2 and '\n' not in res.replace('\r\n', '')
print('10439 枠 %d → %d ／ %s ／ 県 %s' % (len(old['tickets']), len(tickets), new_e['dateLabel'], new_e['prefecture']))
for t in tickets:
    print('  ', t['type'], t.get('date'), t['url'][-22:])
if '--apply' in sys.argv:
    shutil.copyfile(P, 'index.html.bak_0916_goethe')
    with open(P, 'w', encoding='utf-8', newline='') as f:
        f.write(res)
    print('書き込んだ')
