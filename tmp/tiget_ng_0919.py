# gate_tiget_slots の NG を「今朝入れた486件」と「前から載っている分」、消した分に分けて、ズレの型を数える
import re, json, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
rep = open('tmp/gate_tiget_report.txt', encoding='utf-8').read()
h = open('index.html', encoding='utf-8').read()
alive = {e['id'] for e in json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\n\]);', h, re.S).group(1))}
blocks = re.findall(r'🚨 id=(\d+) (.*?)\n((?:    .*\n)+)', rep)
kinds = collections.Counter()
grp = collections.Counter()
for i, name, body in blocks:
    i = int(i)
    g = 'deleted' if i not in alive else ('new486' if 13334 <= i <= 13819 else 'old')
    grp[g] += 1
    if g == 'deleted':
        continue
    only_reg = re.findall(r"登録にだけある: \('(.*?)', '(.*?)', (\w+), (\w+), (\w+)\)", body)
    only_pg = re.findall(r"実ページにだけある: \('(.*?)', '(.*?)', (\w+), (\w+), (\w+)\)", body)
    pg_types = {re.sub(r'\d{1,2}/\d{1,2} \d{1,2}:\d{2}発売〜$', '', t) for t, *_ in only_pg}
    for t, d, a, b2, c in only_reg:
        base = re.sub(r'\d{1,2}/\d{1,2} \d{1,2}:\d{2}発売〜$', '', t)
        if base in pg_types:
            kinds['同じ券種で印が変わった'] += 1
        else:
            kinds['登録にだけある（ページから消えた）'] += 1
    for t, *_ in only_pg:
        base = re.sub(r'\d{1,2}/\d{1,2} \d{1,2}:\d{2}発売〜$', '', t)
        if not any(re.sub(r'\d{1,2}/\d{1,2} \d{1,2}:\d{2}発売〜$', '', x[0]) == base for x in only_reg):
            kinds['実ページにだけある（新しい券種）'] += 1
print(grp)
print(kinds)
print('tail:', rep.strip().splitlines()[-3:])
