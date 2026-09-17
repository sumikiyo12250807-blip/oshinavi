import json, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
b = open('index.html', 'rb').read()
crcrlf = b.count(b'\r\r\n')
bare_lf = len(re.findall(rb'(?<!\r)\n', b))
html = b.decode('utf-8')
EV = json.loads(re.search(r'const EVENTS\s*=\s*(\[[\s\S]*?\]);', html).group(1))
ids = {e['id'] for e in EV}
new = {e['id'] for e in EV if e.get('genre') == 'new'}
no = [int(x) for x in re.search(r'const NEW_ORDER = \[([^\]]*)\]', html).group(1).split(',') if x.strip()]
print(f'エントリ {len(EV)} / CRCRLF {crcrlf} / 素のLF {bare_lf}')
print(f'新着 {len(new)} / NEW_ORDER {len(no)} / NEW_ORDERにあって存在しない {sorted(set(no)-ids)} / 新着なのにNEW_ORDERに無い {sorted(new-set(no))} / NEW_ORDERにあるが新着でない {sorted(set(no)&ids-new)}')
