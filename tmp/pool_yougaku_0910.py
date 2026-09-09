# -*- coding: utf-8 -*-
"""新着プールのうち、ぴあ区分が「音楽/海外ROCK・POPS」のものを並べる。

このジャンルだけ **韓国のアーティストなら kpop に読み替える**
（[[feedback_kpop_vs_yougaku]]・読み替えるのはこの区分のときだけ）。
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
for e in json.loads(m.group(2)):
    if e.get('genre') != 'new':
        continue
    if '海外ROCK' not in (e.get('_piaSub') or ''):
        continue
    print('id=%-5s _genre=%-8s %-44s %s  %s'
          % (e['id'], e.get('_genre'), e['name'][:44], e['date'],
             (e.get('links') or {}).get('pia') or ''))
