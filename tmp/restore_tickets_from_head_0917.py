"""指定 id の tickets を HEAD の index.html の値に戻す（足し算で入った二重枠の取り消し用）。
使い方: python tmp/restore_tickets_from_head_0917.py 2796
"""
import io, json, re, subprocess, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ids = [int(x) for x in sys.argv[1].split(',')]
head = subprocess.run(['git', 'show', 'HEAD:index.html'], capture_output=True).stdout.decode('utf-8')
hev = {e['id']: e for e in json.loads(re.search(r'const EVENTS\s*=\s*(\[[\s\S]*?\]);', head).group(1))}
src = io.open('index.html', encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in src else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
for e in events:
    if e['id'] in ids:
        print(f"id{e['id']} 枠 {len(e['tickets'])} → {len(hev[e['id']]['tickets'])}")
        e['tickets'] = hev[e['id']]['tickets']
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
