# -*- coding: utf-8 -*-
import io, json, sys
sys.path.insert(0, 'C:/Users/user/oshinavi/tools')
import compact_events as C
E = {e['id']: e for e in C.load(io.open('C:/Users/user/oshinavi/index.html', encoding='utf-8', newline='').read())}
e = E[55328]
o = io.open('C:/Users/user/oshinavi/tmp/x1123/x/sm.txt', 'w', encoding='utf-8')
o.write('%s｜%s｜%s｜%s\n%s\n' % (e['name'], e.get('dateLabel'), e.get('venue'), e.get('genre'), e.get('links')))
for t in e['tickets']:
    o.write('%s | date=%s | start=%s | soldout=%s | %s\n' % (t.get('type'), t.get('date'), t.get('startDate'), t.get('soldout'), t.get('url')))
