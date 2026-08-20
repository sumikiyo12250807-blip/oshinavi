# -*- coding: utf-8 -*-
"""削除予定memoryが、他のファイルからどう参照されているかを全部洗う。
[[リンク]]だけでなく素のファイル名も探す（2026-08-10の教訓＝素の名前で裏口復活しかけた）。"""
import os, re, glob, sys
sys.stdout.reconfigure(encoding='utf-8')

MEM = r'C:\Users\user\.claude\projects\C--Users-user-oshinavi\memory'
TARGETS = [
    'feedback_dig_for_official', 'feedback_official_kyoto', 'feedback_far_future_festival_url',
    'feedback_url_only_research', 'project_longrun_anayuki', 'feedback_add_all',
    'user_location', 'reference_oshinavi_seo',
]
scan = glob.glob(os.path.join(MEM, '*.md')) + [
    r'C:\Users\user\oshinavi\PLAYBOOK.md',
]

for t in TARGETS:
    print('=== %s ===' % t)
    hit = 0
    for p in scan:
        if os.path.basename(p) == t + '.md':
            continue
        txt = open(p, encoding='utf-8').read()
        for i, ln in enumerate(txt.splitlines(), 1):
            if t in ln:
                hit += 1
                print('  %s:%d  %s' % (os.path.basename(p), i, ln.strip()[:150]))
    if not hit:
        print('  参照なし')
