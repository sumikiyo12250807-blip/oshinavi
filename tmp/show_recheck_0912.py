# -*- coding: utf-8 -*-
"""再導出結果（scratchpad/recheck_*_result.json）の指定idを表示（読むだけ）。"""
import glob, json, os, sys
sys.stdout.reconfigure(encoding='utf-8')
SP = r'C:\Users\user\AppData\Local\Temp\claude\C--Users-user-oshinavi\0fc1d2b7-fccb-457b-879f-7aec070e018d\scratchpad'
IDS = {int(x) for x in sys.argv[1].split(',')}
for p in sorted(glob.glob(os.path.join(SP, 'recheck_*_result.json'))):
    for r in json.load(open(p, encoding='utf-8')):
        if r['id'] in IDS:
            print('id%s %s [%s]' % (r['id'], r.get('title'), r.get('pia_genre')))
            for s in r.get('shows') or []:
                print('   show %s %s %s' % (s.get('date'), s.get('pref'), s.get('venue')))
            for s in r.get('slots') or []:
                print('   slot %s | %s | %s〜%s | %s' % (s.get('type'), ','.join(s.get('show_dates') or []), s.get('start'), s.get('end'), s.get('state')))
            print('   note %s' % r.get('note'))
