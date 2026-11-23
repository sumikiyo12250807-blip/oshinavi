import os, re, glob, html
D = os.path.dirname(os.path.abspath(__file__))
raw = ''
for p in glob.glob(os.path.join(D, 'raw_*')) + glob.glob(os.path.join(D, 'rec_*')):
    s = open(p, encoding='utf-8', errors='replace').read()
    if p.endswith('.html'):
        s = html.unescape(re.sub(r'<[^>]+>', '', s))
    raw += s + '\n'
norm = lambda s: re.sub(r'\s+', '', s)
rawn = norm(raw)
BAN = r'未就学|歳未満|歳以上有料|手数料|身分証|本人確認|電子チケット|スマチケ|発券|学生証|お支払|クレカ|会員登録|手帳|ぶん|の分|撮影|録音'
for slug in ('kaihonaoto', 'ozonemakoto', 'omiyayoshimoto'):
    t = open(os.path.join(D, slug + '.md'), encoding='utf-8').read()
    lines = t.split('\n')
    body = '\n'.join(lines[5:])
    print(slug, 'body chars', len(body.replace('\n', '')), 'all', len(t.replace('\n', '')))
    print('  ban:', re.findall(BAN, t))
    print('  desutte:', t.count('ですって'))
    for q in re.findall(r'「([^」]+)」', body):
        if norm(q) not in rawn:
            print('  QUOTE NOT FOUND:', q)
    for i, l in enumerate(lines[5:], 6):
        if l and not re.search(r'[。✨てのよわね）」]$', l):
            print('  line end?', i, l[-12:])
