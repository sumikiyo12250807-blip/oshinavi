import re, os, glob
# 取ったページの控えから連絡先のアドレスを消す（tmp も公開されるため）
D = os.path.dirname(os.path.abspath(__file__))
n = 0
for p in glob.glob(os.path.join(D, '*')):
    if not re.search(r'\.(txt|html|md)$', p): continue
    s = open(p, encoding='utf-8', errors='replace', newline='').read()
    t = re.sub(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+', '(address)', s)
    t = re.sub(r'[A-Za-z0-9._%+-]+(&#64;|%40)[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+', '(address)', t)
    if t != s:
        open(p, 'w', encoding='utf-8', newline='').write(t); n += 1
print('scrubbed files', n)
