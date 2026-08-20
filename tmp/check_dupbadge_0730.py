# -*- coding: utf-8 -*-
"""同一バッジが複数枚あるエントリ10件：ぴあ実ページの券種名を引いて席種ラベルの有無を見る"""
import io, json, re, sys, time
sys.path.insert(0, 'tools')
from build_pia_entries import fetch, parse_cards, kenshu

IDS = [1721, 2642, 2805, 2861, 2950, 2953, 2958, 2995, 3347, 3348]

raw = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[.*?\]);', raw, re.S)
M = {e['id']: e for e in json.loads(m.group(1))}

out = []
for eid in IDS:
    ev = M.get(eid)
    if not ev:
        out.append('id=%d ★エントリ無し' % eid)
        continue
    out.append('=== id=%d %s' % (eid, ev.get('artist')))
    out.append('  [登録]')
    for t in ev.get('tickets', []):
        out.append('    %s' % t.get('type'))
    urls = []
    lk = ev.get('links') or {}
    if lk.get('pia'):
        urls.append(lk['pia'])
    for t in ev.get('tickets', []):
        if t.get('url') and t['url'] not in urls:
            urls.append(t['url'])
    seen = set()
    out.append('  [ぴあ原文の券種タイトル]')
    for u in urls[:3]:
        try:
            h = fetch(u)
        except Exception as ex:
            out.append('    ❌FETCH %s' % str(ex)[:80])
            continue
        for c in parse_cards(h):
            if c['state'] not in ('受付中', '発売前'):
                continue
            k = (c.get('title'), c.get('perfdate'), c.get('venue'))
            if k in seen:
                continue
            seen.add(k)
            out.append('    [%s] %s | %s | %s → kenshu=%s' % (
                c['state'], c.get('perfdate'), c.get('venue'), c.get('title'), kenshu(c.get('title') or '')))
        time.sleep(0.5)
    out.append('')

io.open('tmp/out_dupbadge_0730.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('wrote tmp/out_dupbadge_0730.txt')
