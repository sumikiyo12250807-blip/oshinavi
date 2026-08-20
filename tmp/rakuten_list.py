# -*- coding: utf-8 -*-
import sys, json, datetime, re
sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_harvest as R

rows = json.load(open('tmp/rakuten_cand_0725.json', encoding='utf-8'))
today = datetime.date.today().isoformat()
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

print('楽天 候補', len(rows), '件\n')
for r in rows:
    perfs = [p for p in r['perfs'] if (p.get('end') or p['date']) >= today]
    d0 = min(p['date'] for p in perfs) if perfs else '-'
    d1 = max((p.get('end') or p['date']) for p in perfs) if perfs else '-'
    prefs = sorted({p['pref'] for p in perfs})
    # 生きている販売枠
    live = []
    for w in r['windows']:
        f, t = R.win_dates(w['timming'])
        if not f:
            continue
        if t and t < now:
            continue
        live.append('%s[%s〜%s]' % (w['type'], f[5:], (t or '')[5:]))
    print('%-38s | %s〜%s | %s | genre=%-7s | 枠%d: %s' % (
        r['name'][:38], d0[5:], d1[5:], ','.join(prefs)[:16], r['_genre'] or '-', len(live), ' / '.join(live)[:70]))
