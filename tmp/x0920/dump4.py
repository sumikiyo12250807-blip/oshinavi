import re, sys
sys.stdout.reconfigure(encoding='utf-8')
t = open(r'C:\Users\user\oshinavi\index.html', encoding='utf-8').read()
for i in (96, 4436, 11172, 10419):
    m = re.search(r'\n(\s*)\{\s*\n\s*"id": %d,' % i, t)
    if not m:
        print('NOTFOUND', i); continue
    ind = m.group(1)
    end = t.find('\n' + ind + '}', m.end())
    print('=====', i)
    print(t[m.start():end + len(ind) + 2][:6000])
