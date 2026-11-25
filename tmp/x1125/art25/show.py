import re, os, sys, io, html
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
D = os.path.dirname(os.path.abspath(__file__))
# 使い方: show.py 名前 開始の語(無ければ -) 文字数 ...
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
a = sys.argv[1:]
for k in range(0, len(a), 3):
    p = os.path.join(D, 'raw_%s.txt.html' % a[k])
    print('=====', a[k])
    if not os.path.exists(p):
        print(open(os.path.join(D, 'raw_%s.txt' % a[k]), encoding='utf-8').read()[:300]); continue
    s = clean(p)
    i = 0 if a[k + 1] == '-' else max(0, s.find(a[k + 1]))
    print(s[i:i + int(a[k + 2])])
