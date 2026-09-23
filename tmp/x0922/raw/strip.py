import re, sys, html
for fn in sys.argv[1:]:
    s = open(fn, encoding='utf-8', errors='replace').read()
    s = re.sub(r'(?is)<(script|style|noscript)[^>]*>.*?</\1>', ' ', s)
    s = re.sub(r'(?i)<br\s*/?>|</(p|div|li|tr|dt|dd|h\d|th|td)>', '\n', s)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = html.unescape(s)
    lines = [re.sub(r'[ \t　]+', ' ', l).strip() for l in s.split('\n')]
    lines = [l for l in lines if l]
    out = fn.rsplit('.', 1)[0] + '.txt'
    open(out, 'w', encoding='utf-8').write('\n'.join(lines))
    print(out, len(lines))
