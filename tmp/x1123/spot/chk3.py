# -*- coding: utf-8 -*-
import io, re, sys, json, importlib.util
R = 'C:/Users/user/oshinavi/'
sys.path.insert(0, R + 'tools')
import compact_events as C
spec = importlib.util.spec_from_file_location('th', R + 'tools/tiget_harvest.py')
TH = importlib.util.module_from_spec(spec); spec.loader.exec_module(TH)
E = {e['id']: e for e in C.load(io.open(R + 'index.html', encoding='utf-8', newline='').read())}
o = io.open(R + 'tmp/x1123/spot/chk3.txt', 'w', encoding='utf-8')
PAT = re.compile(r'[\w.+-]+[@＠][\w-]+(?:\.[\w-]+)+')
for i in (17058, 30822, 38780, 16922):
    e = E[i]
    urls = sorted({m for t in e['tickets'] + [{'url': e['links'].get('tiget')}] for m in re.findall(r'tiget\.net/events/(\d+)', t.get('url') or '')})
    o.write('\n## id=%s %s｜カード %s %s\n' % (i, PAT.sub('＊', e['name'])[:50], e['date'], e.get('dateLabel')))
    for t in e['tickets']:
        o.write('  枠 %s | %s\n' % (t.get('type'), t.get('date')))
    for u in urls:
        h = TH.fetch('https://tiget.net/events/' + u)
        txt = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', h))
        o.write('  events/%s 終了の文字=%s\n' % (u, 'すでに終了' in txt))
        m = re.search(r'開催日 (.{0,80})', txt)
        o.write('  開催日: %s\n' % (PAT.sub('＊', m.group(1)) if m else '?'))
        d = TH.parse_event(h, u)
        o.write('  公演名: %s\n' % PAT.sub('＊', d.get('name') or ''))
        o.write('  programs: %s\n' % [(p.get('date'), len(p.get('tickets') or [])) for p in d.get('programs') or []])
