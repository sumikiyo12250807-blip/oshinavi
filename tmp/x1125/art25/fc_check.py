import re, glob, datetime, sys, unicodedata
sys.stdout.reconfigure(encoding='utf-8')
D = r'C:/Users/user/oshinavi/tmp/x1125/art25/'
srcs = {}
for f in glob.glob(D + 'fc_*.txt'):
    s = open(f, encoding='utf-8').read()
    s = re.sub(r'(?s)<!--.*?-->', '', s)
    srcs[f.split('\\')[-1].split('/')[-1]] = s
# venue page checked in Chrome separately
def norm(x):
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', x))
out = []
for art in ('harunoutaikai.md', 'mayj_kidsjazz.md', 'tokiasako.md'):
    t = open(D + art, encoding='utf-8').read()
    out.append('### ' + art)
    for q in re.findall(r'「([^」]+)」', t):
        exact = [k for k, v in srcs.items() if q in v]
        loose = [k for k, v in srcs.items() if norm(q) in norm(v)]
        out.append('Q %s | exact=%s | nfkc=%s' % (q, exact[:3], loose[:3]))
    for m in re.finditer(r'(?:R9年\s*)?(\d{1,2})/(\d{1,2})\(([月火水木金土日])\)', t):
        mo, d, w = int(m.group(1)), int(m.group(2)), m.group(3)
        y = 2026 if mo >= 10 else 2027
        real = '月火水木金土日'[datetime.date(y, mo, d).weekday()]
        out.append('D %s -> %d-%02d-%02d %s %s' % (m.group(0), y, mo, d, real, 'OK' if real == w else 'NG'))
    out.append('chars: ' + ' '.join(sorted(set(c for c in t if c in '俱倶'))))
open(D + 'fc_check_out.txt', 'w', encoding='utf-8').write('\n'.join(out))
