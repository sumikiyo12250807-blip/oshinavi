import re, os, sys, io, html
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
D = os.path.dirname(os.path.abspath(__file__))
# 使い方: links.py 名前 正規表現 [名前 正規表現 ...]
a = sys.argv[1:]
for k in range(0, len(a), 2):
    s = open(os.path.join(D, 'raw_%s.txt.html' % a[k]), encoding='utf-8').read()
    print('=====', a[k])
    seen = set()
    for m in re.finditer(r'(?is)<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', s):
        t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', m.group(2)))).strip()
        line = m.group(1) + ' | ' + t[:80]
        if re.search(a[k + 1], line, re.I) and line not in seen:
            seen.add(line); print(line)
