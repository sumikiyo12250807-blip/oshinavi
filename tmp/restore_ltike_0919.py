# ヒールが落としたローチケの一般発売2枠（3568 静岡・4329 宮城）を HEAD から戻す
import io, json, re, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
head = subprocess.run(['git', 'show', 'HEAD:index.html'], capture_output=True).stdout.decode('utf-8')
H = {e['id']: e for e in json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\n\]);', head, re.S).group(1))}
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
by = {e['id']: e for e in events}
for i in (3568, 4329):
    for t in H[i]['tickets']:
        if 'l-tike.com' in (t.get('url') or '') and '9/19 10:00発売' in t['type']:
            if not any(u.get('url') == t['url'] and u['type'] == t['type'] for u in by[i]['tickets']):
                by[i]['tickets'].append(t)
                print('戻した id%d %s' % (i, t['type']))
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
