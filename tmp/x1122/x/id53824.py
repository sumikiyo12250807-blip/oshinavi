# -*- coding: utf-8 -*-
import io, sys, json
sys.path.insert(0, 'C:/Users/user/oshinavi/tools')
import compact_events as C
E = {e['id']: e for e in C.load(io.open('C:/Users/user/oshinavi/index.html', encoding='utf-8', newline='').read())}
o = io.open('C:/Users/user/oshinavi/tmp/x1122/x/id53824.txt', 'w', encoding='utf-8')
for i in (53824, 7729, 5400):
    e = E[i]
    o.write('%s %s ｜ %s ｜ %s\n' % (i, e.get('genre'), e.get('name'), e.get('artist')))
