import sys, collections
sys.stdout.reconfigure(encoding='utf-8')
rows = [l.rstrip('\n').split('\t') for l in open('C:/Users/user/oshinavi/tmp/x0928e/sc_list.txt', encoding='utf-8')]
idx = {r[2] for r in rows if r[0] == 'IDX'}
blt = {r[2] for r in rows if r[0] == 'BLT'}
print('idx', len(idx), 'blt', len(blt), 'overlap', len(idx & blt))
c = collections.Counter()
for r in rows:
    flags = r[9]
    c[(r[0], 'S' in flags, 'X' in flags, 'E' in flags, '-' in flags, int(r[8][5:]) > 1, int(r[7][2:]) > 1)] += 1
for k, v in sorted(c.items()): print(k, v)
# samples of interesting
for r in rows:
    if r[1] in ('24877', '24921', '24635') or 'cluemetic' in r[2]:
        print(r)
