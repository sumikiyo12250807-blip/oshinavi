import re, sys, html
sys.stdout.reconfigure(encoding='utf-8')
for f in sys.argv[1:]:
    b = open(f, 'rb').read()
    for enc in ('utf-8', 'cp932', 'euc-jp'):
        try:
            s = b.decode(enc); break
        except Exception:
            continue
    s = re.sub(r'(?is)<(script|style).*?</\1>', ' ', s)
    s = re.sub(r'<[^>]+>', '\n', s)
    s = html.unescape(s)
    lines = [l.strip() for l in s.splitlines() if l.strip()]
    print('=====', f)
    print('\n'.join(lines))
