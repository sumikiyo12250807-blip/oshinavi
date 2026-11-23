# -*- coding: utf-8 -*-
# 11/27(金)発売の J-POP・ロック（振り分け済み）＝字幕で流す行「HH:MM 名前／県（先行）」を時刻順に
import io, json, re, sys
sys.path.insert(0, 'C:/Users/user/oshinavi/tools')
import compact_events as C
E = C.load(io.open('C:/Users/user/oshinavi/index.html', encoding='utf-8', newline='').read())
D = '2026-11-27'
rows = {}
for e in E:
    if e.get('genre') not in ('jpop', 'rock'):
        continue
    for t in e.get('tickets') or []:
        if t.get('startDate') != D or t.get('soldout'):
            continue
        m = re.search(r'(\d{1,2}:\d{2})発売', t.get('type') or '')
        tm = m.group(1) if m else ''
        name = (e.get('artist') or e.get('name') or '').split('／')[0].strip()
        pref = (e.get('prefecture') or '').split('・')[0]
        pre = '（先行）' if re.search(r'先行|プレリザーブ|プレオーダー|抽選', t.get('type') or '') else ''
        k = (tm.zfill(5), name)
        if k not in rows:
            rows[k] = {'time': tm, 'name': name, 'pref': pref, 'pre': pre, 'genre': e['genre'], 'id': e['id']}
out = [rows[k] for k in sorted(rows)]
json.dump(out, io.open('C:/Users/user/oshinavi/tmp/x1123/songs/rows1127.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
io.open('C:/Users/user/oshinavi/tmp/x1123/songs/rows1127.txt', 'w', encoding='utf-8').write('%d行\n' % len(out) + '\n'.join('%s %s／%s%s ｜%s id%s' % (r['time'], r['name'], r['pref'], r['pre'], r['genre'], r['id']) for r in out))
