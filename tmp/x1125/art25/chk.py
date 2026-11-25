import re, os, sys, io, glob, datetime
# 11/25 記事3本の機械チェック（禁止語・引用が元の文字にあるか・曜日・行末）
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
D = os.path.dirname(os.path.abspath(__file__))
def norm(s):
    s = s.replace('･', '・')
    return re.sub(r'\s+', '', s)
src = ''
for p in glob.glob(os.path.join(D, 'raw_*.txt')) + glob.glob(os.path.join(D, 'fc_*.txt')):
    if p.endswith('.html'):
        continue
    src += norm(open(p, encoding='utf-8', errors='replace').read().replace('\x00', '')) + '\n'
NG = re.compile('未就学|歳未満|歳以上有料|手数料|身分証|本人確認|電子チケット|スマチケ|発券|学生証|お支払|クレカ|会員登録|手帳|ぶん|の分|撮影|録音|ローソン|ローチケ')
W = '月火水木金土日'
out = io.open(os.path.join(D, 'chk.txt'), 'w', encoding='utf-8')
for n in ['harunoutaikai', 'mayj_kidsjazz', 'tokiasako']:
    t = open(os.path.join(D, n + '.md'), encoding='utf-8').read()
    body = t.split('\n\n', 1)[1]
    out.write('===== %s 全体 %d 本文 %d\n' % (n, len(t.replace('\n', '')), len(body.replace('\n', ''))))
    for m in NG.finditer(t): out.write('  NG語 %s\n' % m.group(0))
    for q in re.findall('「([^「」]+)」', t):
        if norm(q) not in src: out.write('  引用が材料に無い: %s\n' % q)
    for line in t.split('\n'):
        for m in re.finditer(r'(R9年 |20\d\d年 ?)?(\d{1,2})/(\d{1,2})\(([月火水木金土日])', line):
            g = m.group(1)
            y = 2027 if g == 'R9年 ' else (int(g[:4]) if g else None)
            mo, d = int(m.group(2)), int(m.group(3))
            cands = [y] if y else [2026, 2027]
            ok = [yy for yy in cands if W[datetime.date(yy, mo, d).weekday()] == m.group(4)]
            if not ok: out.write('  曜日NG %s\n' % m.group(0))
    for line in body.split('\n'):
        if line and not re.search('[。✨！]$', line): out.write('  行末: %s\n' % line)
out.close()
