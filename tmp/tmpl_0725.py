import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = {e['id']: e for e in json.loads(m.group(2))}
for i in (3171, 3209):
    print(json.dumps(EV[i], ensure_ascii=False, indent=1))
    print('---')
