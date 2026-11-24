import re, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
D = os.path.dirname(os.path.abspath(__file__))
for n in ['amami2', 'uzaki104', 'uzaki105', 'uzaki106', 'uzaki107', 'uzaki099']:
    s = open(os.path.join(D, 'raw_ep_%s.txt' % n), encoding='utf-8').read()
    a = s.find('公演日や地域を指定して')
    b = s.find('受付は全て終了しました')
    print('=====', n)
    print(s[a:b])
for n in ['amami1', 'nagoya', 'uzaki103']:
    h = open(os.path.join(D, 'raw_ep_%s.txt.html' % n), encoding='utf-8').read()
    print('=====', n, len(h))
    for m in re.finditer(r'.{0,80}(円|料金|主催|お問い合わせ|問合).{0,120}', h):
        t = m.group(0)
        if '手数料' in t or '納得の料金' in t or '開演時間や料金' in t: continue
        print(t[:220])
