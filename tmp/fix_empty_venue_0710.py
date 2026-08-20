# -*- coding: utf-8 -*-
"""「全国ツアー（）」の空カッコ会場をぴあ機械パースで埋める（venueのみ更新）。"""
import re, json, sys, io, time
sys.path.insert(0, 'tools')
from build_pia_entries import build
out = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DRY = '--apply' not in sys.argv

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
targets = [e for e in EVENTS if '（）' in (e.get('venue') or '')]
out.write(f'空カッコ会場 {len(targets)}件\n'); out.flush()
n = 0
for e in targets:
    urls = []
    p = (e.get('links') or {}).get('pia')
    if p and 'pia' in p: urls.append(p)
    for t in e.get('tickets', []):
        u = t.get('url')
        if u and 'pia' in u and u not in urls: urls.append(u)
    if not urls:
        out.write(f"  id={e['id']} {e['artist'][:20]} ぴあURL無し→手当て要\n"); continue
    try:
        ne = build({'newid': e['id'], 'artist': e.get('artist', ''), 'urls': urls})
    except Exception as ex:
        out.write(f"  id={e['id']} ERROR {str(ex)[:60]}\n"); time.sleep(2); continue
    if ne and ne.get('venue') and '（）' not in ne['venue']:
        out.write(f"  id={e['id']} {e['artist'][:20]}\n     {e['venue']}  ->  {ne['venue']}\n")
        e['venue'] = ne['venue']
        if ne.get('prefecture'): e['prefecture'] = ne['prefecture']
        n += 1
    else:
        out.write(f"  id={e['id']} {e['artist'][:20]} ぴあでも会場取れず\n")
    out.flush()
    time.sleep(1.2)
out.write(f'=== {n}件 修正 ===\n')
if DRY:
    out.write('(DRY)\n')
elif n:
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open('index.html.bak_0710_venue','w',encoding='utf-8').write(h)
    open('index.html','w',encoding='utf-8').write(h[:m.start()]+m.group(1)+new_arr+m.group(3)+h[m.end():])
    out.write('written\n')
out.flush()
