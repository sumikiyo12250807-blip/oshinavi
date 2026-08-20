# -*- coding: utf-8 -*-
"""ChromeのlocalStorage(leveldb)から oshinavi_memory_audit の判定JSONを拾う。
leveldbは読むだけ（非破壊）。値はUTF-16LEで格納されることがあるので両方試す。"""
import os, re, glob, json, sys
sys.stdout.reconfigure(encoding='utf-8')

base = os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data\Default\Local Storage\leveldb')
files = sorted(glob.glob(os.path.join(base, '*')), key=os.path.getmtime, reverse=True)
print('leveldbファイル', len(files))

blobs = []
for p in files:
    if os.path.isdir(p):
        continue
    try:
        b = open(p, 'rb').read()
    except Exception as e:
        print('  読めない', os.path.basename(p), e); continue
    if b'oshinavi_memory_audit' in b:
        print('  ヒット:', os.path.basename(p), len(b))
        blobs.append((p, b))

pat = re.compile(rb'\{(?:[^{}]|\{[^{}]*\})*\}')
for p, b in blobs:
    for enc in ('utf-8', 'utf-16-le'):
        try:
            t = b.decode(enc, 'ignore')
        except Exception:
            continue
        for m in re.finditer(r'\{\s*"[^"]+"\s*:\s*"(?:iru|iranai|tougou|いる|いらない|統合)"', t):
            s = t[m.start():m.start() + 20000]
            depth, end = 0, None
            for i, ch in enumerate(s):
                if ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        end = i + 1
                        break
            if end:
                try:
                    d = json.loads(s[:end])
                except Exception:
                    continue
                print('=== %s (%s) 判定 %d件 ===' % (os.path.basename(p), enc, len(d)))
                print(json.dumps(d, ensure_ascii=False, indent=1))
                sys.exit(0)
print('判定JSONは見つからなかった')
