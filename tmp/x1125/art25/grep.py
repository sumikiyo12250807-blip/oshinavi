import re, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
D = os.path.dirname(os.path.abspath(__file__))
# 使い方: grep.py 名前 正規表現 前後の文字数 ...  （生HTMLから前後つきで出す）
a = sys.argv[1:]
for k in range(0, len(a), 3):
    s = open(os.path.join(D, 'raw_%s.txt.html' % a[k]), encoding='utf-8').read()
    n = int(a[k + 2])
    print('=====', a[k], len(s))
    c = 0
    for m in re.finditer(a[k + 1], s):
        print('--', re.sub(r'\s+', ' ', s[max(0, m.start() - n):m.end() + n]))
        c += 1
        if c >= 12: break
