import sys, urllib.request, re, html, time, os
D = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:]
for k in range(0, len(args), 2):
    url, out = args[k], os.path.join(D, args[k + 1])
    if k: time.sleep(4)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36', 'Accept-Language': 'ja'})
    try:
        b = urllib.request.urlopen(req, timeout=30).read()
    except Exception as e:
        open(out, 'w', encoding='utf-8').write('ERR ' + repr(e)); continue
    s = None
    for enc in ('utf-8', 'cp932', 'euc-jp'):
        try:
            s = b.decode(enc); break
        except Exception:
            continue
    if s is None: s = b.decode('utf-8', 'replace')
    open(out + '.html', 'w', encoding='utf-8').write(s)
    s = re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>', ' ', s)
    s = re.sub(r'(?i)<br\s*/?>|</p>|</div>|</li>|</tr>|</h\d>|</dd>|</dt>|</td>|</th>', '\n', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = html.unescape(s)
    s = re.sub(r'[ \t\r　]+', ' ', s)
    s = re.sub(r'\n\s*\n+', '\n', s)
    open(out, 'w', encoding='utf-8').write(s)
    print(out, len(s))
