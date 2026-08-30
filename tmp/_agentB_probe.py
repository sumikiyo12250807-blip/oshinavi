import re, sys, io

h = open('C:/Users/user/oshinavi/tmp/_agentB_test.html', 'rb').read()
try:
    s = h.decode('utf-8')
    enc = 'utf-8 ok'
except Exception as e:
    s = h.decode('utf-8', 'replace')
    enc = 'utf-8 err: %s' % e

out = io.open('C:/Users/user/oshinavi/tmp/_agentB_probe.txt', 'w', encoding='utf-8')
out.write(enc + '\n=====\n')
for kw in ['breadcrumb', 'itemListElement', '出演', 'genre', 'ジャンル']:
    for m in list(re.finditer(re.escape(kw), s))[:4]:
        a = max(0, m.start() - 200)
        out.write('--- %s ---\n' % kw)
        out.write(s[a:m.start() + 400].replace('\n', ' ') + '\n')
out.close()
print('done')
