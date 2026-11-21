import re, os, glob, datetime, sys
sys.stdout.reconfigure(encoding='utf-8')
D = os.path.dirname(os.path.abspath(__file__))
raw = ''
for f in glob.glob(os.path.join(D, '*.txt')) + glob.glob(os.path.join(D, '*.html')):
    try:
        raw += open(f, encoding='utf-8').read()
    except Exception:
        pass
rawn = re.sub(r'\s+', '', raw)
NG = re.compile('未就学|歳未満|歳以上有料|手数料|身分証|本人確認|電子チケット|スマチケ|発券|学生証|お支払|クレカ|会員登録|手帳|ぶん|の分|撮影|録音|ドリンク')
W = '月火水木金土日'
for slug in ('montecristo', 'watanabemisato', 'hitofuji'):
    s = open(os.path.join(D, slug + '.md'), encoding='utf-8').read()
    body = s.split('\n\n', 1)[1]
    print('==', slug, 'body', len(body.replace('\n', '')), 'all', len(s.replace('\n', '')))
    print(' NG:', NG.findall(s))
    for q in re.findall('「([^「」]+)」', s):
        ok = re.sub(r'\s+', '', q) in rawn
        if not ok: print(' QUOTE NOT FOUND:', q)
    for m in re.finditer(r'(R9年 )?(\d{1,2})/(\d{1,2})\((.)', s):
        mo, d = int(m.group(2)), int(m.group(3))
        y = 2027 if mo <= 6 else 2026
        w = W[datetime.date(y, mo, d).weekday()]
        if w != m.group(4): print(' WEEKDAY NG:', m.group(0), w)
    if '@' in s: print(' AT MARK')
print('done')
