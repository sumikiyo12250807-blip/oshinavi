# -*- coding: utf-8 -*-
import io, re, sys, urllib.request
sys.path.insert(0, 'C:/Users/user/oshinavi/tools')
import importlib.util
spec = importlib.util.spec_from_file_location('th', 'C:/Users/user/oshinavi/tools/tiget_harvest.py')
TH = importlib.util.module_from_spec(spec); spec.loader.exec_module(TH)
o = io.open('C:/Users/user/oshinavi/tmp/x1123/spot/chk37549.txt', 'w', encoding='utf-8')
h = TH.fetch('https://tiget.net/events/531971')
txt = re.sub(r'<[^>]+>', ' ', h)
txt = re.sub(r'\s+', ' ', txt)
for k in ('すでに終了', '開催日', '2026', '12月5', '12/5', '11/13', '11月13'):
    for m in re.finditer(re.escape(k), txt):
        o.write('%s: …%s…\n' % (k, txt[max(0, m.start() - 40):m.end() + 60]))
        break
d = TH.parse_event(h, '531971')
o.write('programs: %r\n' % [(p.get('date'), [t.get('name') for t in p.get('tickets') or []]) for p in d.get('programs') or []])
