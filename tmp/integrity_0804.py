# -*- coding: utf-8 -*-
"""index.html の健全性チェック: 件数 / 孤立LF(CRLFでないLF) / JSONパース可否。"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, 'index.html')
raw = open(p, 'rb').read()
stray = raw.count(b'\n') - raw.count(b'\r\n')
h = raw.decode('utf-8')
m = re.search(r'const\s+EVENTS\s*=\s*(\[.*?\]);\s*\n', h, re.S)
ev = json.loads(m.group(1))
ids = [e['id'] for e in ev]
print('entries=%d  unique_ids=%d  stray_lf=%d' % (len(ev), len(set(ids)), stray))
gone = [i for i in [491, 976, 1689, 1970, 2656, 2695, 1404, 1774, 2038, 2663, 2845, 3485] if i in set(ids)]
print('still_present=%s' % gone)
