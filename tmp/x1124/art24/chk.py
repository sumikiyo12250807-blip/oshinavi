import re, os, sys, io, glob, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
D = os.path.dirname(os.path.abspath(__file__))
def norm(s):
    s = s.replace('･', '・')
    return re.sub(r'\s+', '', s)
src = ''
for p in glob.glob(os.path.join(D, 'raw_*.nc.txt')):
    src += norm(open(p, encoding='utf-8').read().replace('\x00', '')) + '\n'
NG = re.compile('未就学|歳未満|歳以上有料|手数料|身分証|本人確認|電子チケット|スマチケ|発券|学生証|お支払|クレカ|会員登録|手帳|ぶん|の分|撮影|録音')
W = '月火水木金土日'
for n in ['amamitomochika', 'uzakiryudo', 'nagoyaongakusai']:
    t = open(os.path.join(D, n + '.md'), encoding='utf-8').read()
    body = t.split('\n\n', 1)[1]
    print('=====', n, '全体', len(t.replace('\n', '')), '本文', len(body.replace('\n', '')))
    for m in NG.finditer(t): print('  NG語', m.group(0))
    for q in re.findall('「([^「」]+)」', t):
        if norm(q) not in src: print('  引用が材料に無い:', q)
    for line in t.split('\n'):
        for m in re.finditer(r'(R9年 |20\d\d年 )?(\d{1,2})/(\d{1,2})\(([月火水木金土日])', line):
            y = 2027 if m.group(1) == 'R9年 ' else (int(m.group(1)[:4]) if m.group(1) else None)
            mo, d = int(m.group(2)), int(m.group(3))
            cands = [y] if y else [2026, 2027]
            ok = [yy for yy in cands if W[datetime.date(yy, mo, d).weekday()] == m.group(4)]
            print('  曜日', m.group(0), 'OK' if ok else 'NG', ok)
    for line in body.split('\n'):
        if line and not re.search('[。✨！]$', line) : print('  行末:', line)
print(W[datetime.date(2023, 12, 14).weekday()], W[datetime.date(2027, 9, 23).weekday()])
