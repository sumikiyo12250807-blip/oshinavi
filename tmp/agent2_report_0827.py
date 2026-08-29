# -*- coding: utf-8 -*-
import io, json, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
d = json.load(io.open(r'C:\Users\user\oshinavi\tmp\agent2_result_0827.json', encoding='utf-8'))
for r in d:
    print('=== %d  %s' % (r['no'], r['url']))
    print('  TITLE: %s' % r['title'])
    if r['error']:
        print('  ERROR: %s' % r['error'])
    if r['confirm']:
        print('  CONFIRM: %s' % ' | '.join(r['confirm']))
    for c in r['cards']:
        print('  - [%s|%s] %s | %s | %s %s | %s | %s' % (
            c['state'], c['statustext'], c['title'], c['when'],
            c['perfdate'], ('~' + c['perf_end']) if c['perf_end'] != c['perfdate'] else '',
            c['pref'] + ' ' + c['venue'], c['url']))
    for k in r['children']:
        print('  CHILD %s %s err=%s' % (k['url'], k['title'], k['error']))
        for c in k['cards']:
            print('    - [%s|%s] %s | %s | %s %s | %s | %s' % (
                c['state'], c['statustext'], c['title'], c['when'],
                c['perfdate'], ('~' + c['perf_end']) if c['perf_end'] != c['perfdate'] else '',
                c['pref'] + ' ' + c['venue'], c['url']))
