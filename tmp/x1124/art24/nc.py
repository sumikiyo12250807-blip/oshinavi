import re, os, sys, io, html, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
D = os.path.dirname(os.path.abspath(__file__))
def clean(p):
    s = open(p, encoding='utf-8').read()
    s = re.sub(r'(?s)<!--.*?-->', ' ', s)
    s = re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>', ' ', s)
    s = re.sub(r'(?i)<br\s*/?>|</p>|</div>|</li>|</tr>|</h\d>|</dd>|</dt>|</td>|</th>', '\n', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = html.unescape(s)
    s = re.sub(r'[ \t\r　]+', ' ', s)
    s = re.sub(r'\n\s*\n+', '\n', s)
    return s
for p in glob.glob(os.path.join(D, 'raw_*.txt.html')):
    open(p[:-9] + '.nc.txt', 'w', encoding='utf-8').write(clean(p))
for n in sys.argv[1:]:
    print('=====', n)
    print(open(os.path.join(D, 'raw_%s.nc.txt' % n), encoding='utf-8').read()[:3500])
