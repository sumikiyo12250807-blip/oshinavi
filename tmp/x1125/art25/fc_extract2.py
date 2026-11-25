import sys, json, re, html
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(open(r'C:/Users/user/oshinavi/tmp/x1125/art25/fc_yoko_3675json.txt.html', encoding='utf-8'))
out = []
for k, v in d.items():
    if isinstance(v, str):
        t = re.sub(r'[ \t\r\n　]+', ' ', html.unescape(re.sub(r'<[^>]+>', ' | ', v)))
        out.append('## ' + k + '\n' + t)
open(r'C:/Users/user/oshinavi/tmp/x1125/art25/fc_yoko_3675_plain.txt', 'w', encoding='utf-8').write('\n'.join(out))
print(len(out))
