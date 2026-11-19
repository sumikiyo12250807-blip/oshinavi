import sys, re, os
D = os.path.dirname(os.path.abspath(__file__))
pat = re.compile(sys.argv[1], re.I)
for f in sys.argv[2:]:
    s = open(os.path.join(D, f), encoding='utf-8').read()
    seen = set()
    for m in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', s, re.S):
        u, t = m.group(1), re.sub(r'<[^>]+>|\s+', ' ', m.group(2)).strip()
        if pat.search(u + ' ' + t) and u not in seen:
            seen.add(u)
            print(f, u, t[:80])
