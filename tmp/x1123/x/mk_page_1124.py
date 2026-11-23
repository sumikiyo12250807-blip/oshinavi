# -*- coding: utf-8 -*-
# 11/24発売の X → all_1124.txt ＋ 携帯で読む確認ページ xcheck_1124.html（x1122 の mk_page_1123 の形・🆕15分おき）
import io, os, glob
X = 'C:/Users/user/oshinavi/tmp/x1123/x/'
names = sorted(os.path.basename(f)[:-4] for f in glob.glob(X + 'post/*.txt'))
ORD = [n for n in names if n.startswith('trend')] + [n for n in names if n.startswith('mat')] + [n for n in names if n.startswith('shu')]
TM = []
h, m = 19, 31
for _ in ORD:
    TM.append('%d:%02d' % (h, m))
    m += 15
    if m >= 60:
        h, m = h + 1, m - 60
NOTES = io.open(X + 'page_notes_1124.txt', encoding='utf-8').read().strip().splitlines() if os.path.exists(X + 'page_notes_1124.txt') else []
VIDS = {}
if os.path.exists(X + 'page_vids_1124.txt'):
    for l in io.open(X + 'page_vids_1124.txt', encoding='utf-8').read().strip().splitlines():
        k, v = l.split('\t', 1)
        VIDS[k] = v
s = io.open('C:/Users/user/oshinavi/tmp/x1120/x/mk_page_1121.py', encoding='utf-8').read()
s = '\n'.join(l for l in s.split('\n') if not l.startswith('# '))
a = s.index('ORDER = ')
b = s.index("CSS = '''")
head = 'ORDER = %r\nTIMES = %r\nVID = %r\nNOTES = %r\n' % (ORD, TM, VIDS, NOTES)
s = s[:a] + head + s[b:]
s = s.replace("X = 'C:/Users/user/oshinavi/tmp/x1120/x/'", "X = 'C:/Users/user/oshinavi/tmp/x1123/x/'")
s = s.replace('11/21発売 確認用', '11/24発売 確認用').replace('all_1121', 'all_1124').replace('xcheck_1121', 'xcheck_1124')
s = s.replace('11/21(土)発売の X 11本', '11/24(火)発売の X %d本' % len(ORD))
s = s.replace("t.replace('明日発売の', '')", "t.replace('明日発売の', '').replace('のチケット 発売中', '')")
assert 'x1120' not in s and '1121' not in s, [l for l in s.splitlines() if '1121' in l]
exec(compile(s, 'page', 'exec'))
