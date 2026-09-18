# -*- coding: utf-8 -*-
import io, json
d = json.load(io.open(r'C:\Users\user\oshinavi\tmp\tiget_wide_0918.json', encoding='utf-8'))
print('top keys', list(d.keys()))
print('events', len(d['events']))
ev = d['events'][0]
print('event keys', list(ev.keys()))
out = io.open(r'C:\Users\user\oshinavi\tmp\audit_raw_sample.json','w',encoding='utf-8')
json.dump(d['events'][:2], out, ensure_ascii=False, indent=1)
out.close()
print(io.open(r'C:\Users\user\oshinavi\tmp\audit_raw_sample.json',encoding='utf-8').read()[:3000])
