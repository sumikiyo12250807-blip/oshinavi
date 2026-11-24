import re, html, glob, io, sys, os, unicodedata
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
D = os.path.dirname(os.path.abspath(__file__))
def vis(p):
    s = open(p, encoding='utf-8').read()
    s = re.sub(r'(?s)<!--.*?-->', ' ', s)
    s = re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>', ' ', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = html.unescape(s)
    return re.sub(r'\s+', '', s)
def vis_all(p):  # script/json 含む（コメントは除く）
    s = open(p, encoding='utf-8').read()
    s = re.sub(r'(?s)<!--.*?-->', ' ', s)
    s = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), s)
    s = s.replace('\\n', '')
    s = re.sub(r'<[^>]+>', '', s)
    s = html.unescape(s)
    return re.sub(r'\s+', '', s)
pages = {os.path.basename(p): (vis(p), vis_all(p)) for p in glob.glob(os.path.join(D, 'fc_*.html'))}
N = lambda x: unicodedata.normalize('NFKC', x)
out = []
for art in ('amamitomochika.md', 'uzakiryudo.md', 'nagoyaongakusai.md'):
    t = open(os.path.join(D, art), encoding='utf-8').read()
    out.append('### ' + art)
    for q in re.findall(r'「([^」]+)」', t):
        qq = re.sub(r'\s+', '', q)
        strict = [k for k, (a, b) in pages.items() if qq in a]
        strict2 = [k for k, (a, b) in pages.items() if qq in b and k not in strict]
        loose = [k for k, (a, b) in pages.items() if N(qq) in N(b) and k not in strict and k not in strict2]
        out.append(f'「{q}」 本文一致={strict[:3]} スクリプト内一致={strict2[:2]} 正規化一致のみ={loose[:3]}')
open(os.path.join(D, 'fc_quotecheck.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(out))
