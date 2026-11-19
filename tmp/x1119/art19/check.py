import os, re, glob, html
D = os.path.dirname(os.path.abspath(__file__))
src = {}
for f in glob.glob(os.path.join(D, '*.html')):
    s = open(f, encoding='utf-8').read()
    s = re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>', ' ', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = html.unescape(s)
    s = re.sub(r'\s+', '', s)
    src[os.path.basename(f)] = s
BAN = r'未就学|歳未満|歳以上有料|手数料|身分証|本人確認|電子チケット|スマチケ|発券|学生証|お支払|クレカ|会員登録|手帳|ぶん|の分|撮影|録音|ドリンク'
out = []
for slug in ['daibakushow', 'asagaya', 'plastictree']:
    t = open(os.path.join(D, slug + '.md'), encoding='utf-8').read()
    body = t.split('\n\n', 1)[1]
    out.append(f'== {slug} 全体{len(t.replace(chr(10), ""))}字 本文{len(body.replace(chr(10), ""))}字')
    for m in re.finditer(BAN, t):
        out.append(f'  BAN {m.group()} @ {t[max(0, m.start()-15):m.end()+15]!r}')
    for q in re.findall(r'「([^「」]+)」', t):
        k = re.sub(r'\s+', '', q)
        hit = [n for n, s in src.items() if k in s]
        out.append(f'  {"OK" if hit else "NG"} 「{q}」 {hit[:3]}')
open(os.path.join(D, 'check_out.txt'), 'w', encoding='utf-8').write('\n'.join(out))
