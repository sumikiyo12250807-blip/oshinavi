# -*- coding: utf-8 -*-
# Downloads の新しいファイル（11/11 15時以降）を時刻順に
import os, sys, time
sys.stdout.reconfigure(encoding='utf-8')
DL = 'C:/Users/user/Downloads/'
rows = []
for f in os.listdir(DL):
    p = DL + f
    m = os.path.getmtime(p)
    if m > time.mktime((2026, 11, 11, 12, 0, 0, 0, 0, -1)):
        rows.append((m, f, os.path.getsize(p)))
for m, f, s in sorted(rows):
    print(time.strftime('%H:%M:%S', time.localtime(m)), s, repr(f))
