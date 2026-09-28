import sys, re, os, html as H
sys.stdout.reconfigure(encoding='utf-8')
d = 'C:/Users/user/oshinavi/tmp/x0928e/sc_html/'
o = 'C:/Users/user/oshinavi/tmp/x0928e/sc_txt/'
os.makedirs(o, exist_ok=True)
for fn in os.listdir(d):
    s = open(d + fn, encoding='utf-8').read()
    ld = re.findall(r'<script[^>]*ld\+json[^>]*>(.*?)</script>', s, re.S)
    s2 = re.sub(r'<(script|style|noscript)[^>]*>.*?</\1>', ' ', s, flags=re.S)
    s2 = re.sub(r'<br\s*/?>', '\n', s2)
    s2 = re.sub(r'<[^>]+>', '\n', s2)
    s2 = H.unescape(s2)
    lines = [l.strip() for l in s2.split('\n')]
    lines = [l for l in lines if l]
    open(o + fn[:-5] + '.txt', 'w', encoding='utf-8').write('LDJSON:' + '\n'.join(x.strip() for x in ld) + '\n=====\n' + '\n'.join(lines))
