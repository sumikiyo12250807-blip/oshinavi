import re
s = open(r'C:\Users\user\oshinavi\index.html', encoding='utf-8').read()
out = []
for i in ['54893', '54576', '43595']:
    m = re.search(r'["\']?id["\']?\s*:\s*' + i + r'\b', s)
    out.append('### ' + i)
    if m:
        st = s.rfind('{', 0, m.start())
        out.append(s[st:st + 4000])
open(r'C:\Users\user\oshinavi\tmp\x1118\art18\dump3.txt', 'w', encoding='utf-8').write('\n'.join(out))
