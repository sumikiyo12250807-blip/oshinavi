import sys, json, re, html
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(open(r'C:/Users/user/oshinavi/tmp/x1125/art25/fc_yoko_ticketjson.txt.html', encoding='utf-8'))
out = []
for k, v in d.items():
    t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' | ', v)))
    i = t.find('土岐')
    if i >= 0:
        out.append(k + '\n' + t[max(0, i - 700):i + 1500])
    for u in re.findall(r'href="([^"]+)"', v):
        if 'detail' in u:
            out.append('LINK ' + k + ' ' + u)
open(r'C:/Users/user/oshinavi/tmp/x1125/art25/fc_yoko_toki_extract.txt', 'w', encoding='utf-8').write('\n'.join(out))
print(len(out))
