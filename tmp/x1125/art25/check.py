import re, os, sys, io, glob, html
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
D = os.path.dirname(os.path.abspath(__file__))
BAD = r'未就学|歳未満|歳以上有料|手数料|身分証|本人確認|電子チケット|スマチケ|発券|学生証|お支払|クレカ|会員登録|手帳|ぶん|の分|撮影|録音'
def norm(s):
    s = html.unescape(re.sub(r'<[^>]+>', '', s))
    return re.sub(r'\s+', '', s)
raw = {}
for p in glob.glob(os.path.join(D, 'raw_*')):
    if p.endswith('.pdf'): continue
    try:
        raw[os.path.basename(p)] = norm(open(p, encoding='utf-8').read())
    except Exception as e:
        pass
for slug in ('harunoutaikai', 'mayj_kidsjazz', 'tokiasako'):
    t = open(os.path.join(D, slug + '.md'), encoding='utf-8').read()
    print('=====', slug, '字数', len(t.replace('\n', '')), ' 本文だけ', len(''.join(t.split('\n')[5:])))
    print(' 禁止語:', re.findall(BAD, t))
    print(' ですって:', len(re.findall('ですって', t)), ' 2027:', len(re.findall('2027年', t)))
    for i, l in enumerate(t.split('\n')[5:], 6):
        if l and not re.search(r'[。✨]$', l): print(' 行末が。でない:', i, l)
    for q in re.findall(r'「([^「」]+)」', t):
        hit = [n for n, s in raw.items() if norm(q) in s]
        print('  ', 'OK' if hit else 'NG', q, '->', hit[:2])
