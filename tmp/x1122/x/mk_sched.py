# -*- coding: utf-8 -*-
# 11/23 発売の X 5本：指紋（post_hash.txt）と予約の JS（js_<名>.txt）を x1121 の形で作る
import io, glob, hashlib, re, os, unicodedata, subprocess, sys
X = 'C:/Users/user/oshinavi/tmp/x1122/x/'
o = io.open(X + 'post_hash.txt', 'w', encoding='utf-8')
for f in sorted(glob.glob(X + 'post/*.txt')):
    t = io.open(f, encoding='utf-8').read()
    h = hashlib.sha256(re.sub(r'\s', '', t).encode('utf-8')).hexdigest()
    odd = [c for c in t if c in '\u3099\u309a\u200d' or '\uff61' <= c <= '\uff9f']
    nfc = unicodedata.normalize('NFC', t) != t
    o.write('%s %s 字数%d 変わった字%s NFC違い%s 頭=%s\n' % (os.path.basename(f), h, len(t), odd or 'なし', nfc, t.strip().splitlines()[0][:30]))
o.close()
s = io.open('C:/Users/user/oshinavi/tmp/x1121/x/mkjs.py', encoding='utf-8').read().replace('tmp/x1121/x/', 'tmp/x1122/x/')
io.open(X + 'mkjs.py', 'w', encoding='utf-8').write(s)
for a in [['trend01', '19', '31'], ['mat01', '19', '41'], ['mat02', '19', '51', 'v'], ['mat03', '20', '01', 'v'], ['shu01', '20', '11']]:
    subprocess.run([sys.executable, X + 'mkjs.py'] + a, check=True)
print(io.open(X + 'post_hash.txt', encoding='utf-8').read())
