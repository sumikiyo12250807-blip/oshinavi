# -*- coding: utf-8 -*-
"""Edgeのleveldbから oshinavi_memory_audit の判定JSON（keep/drop/merge）を取り出す（読むだけ）。"""
import re, json, sys, glob, os
sys.stdout.reconfigure(encoding='utf-8')

paths = sorted(glob.glob(os.path.expandvars(
    r'%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Local Storage\leveldb\*')),
    key=os.path.getmtime, reverse=True)

best = None
for p in paths:
    if os.path.isdir(p):
        continue
    try:
        b = open(p, 'rb').read()
    except Exception:
        continue
    if b'oshinavi_memory_audit' not in b:
        continue
    for enc in ('utf-8', 'utf-16-le'):
        t = b.decode(enc, 'ignore')
        for m in re.finditer(r'\{"[A-Za-z0-9_]+":"(?:keep|drop|merge)"', t):
            s = t[m.start():]
            depth = 0
            for i, ch in enumerate(s[:100000]):
                if ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        try:
                            d = json.loads(s[:i + 1])
                        except Exception:
                            d = None
                        if d and (best is None or len(d) > len(best[1])):
                            best = (os.path.basename(p) + '/' + enc, d)
                        break

if not best:
    print('判定は見つからなかった')
    raise SystemExit(1)

src, d = best
lab = {'keep': 'いる', 'drop': 'いらない', 'merge': '統合'}
print('=== 判定 %d件 (%s) ===' % (len(d), src))
for v in ('drop', 'merge', 'keep'):
    ls = sorted(k for k in d if d[k] == v)
    print('【%s】%d件' % (lab[v], len(ls)))
    for s in ls:
        print('  ' + s)
json.dump(d, open('tmp/audit_marks.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
