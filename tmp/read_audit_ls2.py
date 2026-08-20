# -*- coding: utf-8 -*-
"""Chrome/Edge の全プロファイルの localStorage から oshinavi_memory_audit を探す（読むだけ）。"""
import os, glob, sys
sys.stdout.reconfigure(encoding='utf-8')

roots = [
    os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data'),
    os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\Edge\User Data'),
    os.path.expandvars(r'%APPDATA%\Mozilla\Firefox\Profiles'),
]
needle = b'oshinavi_memory_audit'
hits = []
for r in roots:
    if not os.path.isdir(r):
        print('無し:', r); continue
    n = 0
    for p in glob.glob(os.path.join(r, '**', '*'), recursive=True):
        if not os.path.isfile(p):
            continue
        base = os.path.basename(p)
        if not (base.endswith('.log') or base.endswith('.ldb') or base.endswith('.sqlite')
                or base == 'CURRENT' or base.startswith('MANIFEST')):
            continue
        n += 1
        try:
            b = open(p, 'rb').read()
        except Exception:
            continue
        if needle in b:
            hits.append(p)
            print('ヒット:', p, len(b))
    print('走査 %d ファイル: %s' % (n, r))
print('ヒット合計', len(hits))
