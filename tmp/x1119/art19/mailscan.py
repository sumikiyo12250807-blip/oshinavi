import os, re, glob
D = os.path.dirname(os.path.abspath(__file__))
pat = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
hits = []
for f in glob.glob(os.path.join(D, '*')):
    if os.path.isdir(f) or f.endswith('.py'):
        continue
    s = open(f, encoding='utf-8', errors='replace').read()
    m = pat.findall(s)
    if m:
        hits.append(os.path.basename(f))
        open(f, 'w', encoding='utf-8').write(pat.sub('[mail]', s))
open(os.path.join(D, 'mailscan_out.txt'), 'w', encoding='utf-8').write('\n'.join(hits))
print(len(hits))
