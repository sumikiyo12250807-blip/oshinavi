# -*- coding: utf-8 -*-
"""既存ツアーエントリの形（dateLabel/venue/prefecture/per-ticket url）を確認する。
コンソールの文字化けを目で読まないため、Pythonから直接出す。"""
import io, re, sys, json
sys.stdout.reconfigure(encoding='utf-8')
idx = io.open('index.html', encoding='utf-8').read()
EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', idx, re.S).group(2))
for eid in (4435, 4426, 4458):
    e = [x for x in EV if x['id'] == eid][0]
    print('=== %d %s' % (eid, e['artist']))
    for k in ('date', 'dateLabel', 'venue', 'prefecture'):
        print('   %-11s %s' % (k, e.get(k)))
    for t in e.get('tickets') or []:
        print('   枠 type=%s' % t.get('type'))
        print('      date=%s start=%s url=%s' % (t.get('date'), t.get('startDate'), t.get('url')))
m = re.search(r'const NEW_ORDER = (\[[^\]]*\])', idx)
print()
print('NEW_ORDER =', m.group(1) if m else '(見つからない)')
