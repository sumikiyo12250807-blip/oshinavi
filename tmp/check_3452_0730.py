# -*- coding: utf-8 -*-
"""3452 反田恭平: ぴあ原文の券種名を確認（カッコ不均衡の真因）"""
import io, json, re, sys, subprocess

raw = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[.*?\]);', raw, re.S)
arr = json.loads(m.group(1))
ev = [e for e in arr if e['id'] == 3452][0]

out = ['id=3452 %s' % ev.get('artist')]
out.append('links: %s' % json.dumps(ev.get('links'), ensure_ascii=False))
for t in ev.get('tickets', []):
    out.append('  枠: %r | date=%s' % (t.get('type'), t.get('date')))

url = (ev.get('links') or {}).get('pia')
out.append('')
out.append('=== ぴあ生ページの券種名（pia_tickets.py --all）')
r = subprocess.run([sys.executable, 'tools/pia_tickets.py', url, '--all'],
                   capture_output=True)
out.append(r.stdout.decode('utf-8', 'replace'))
if r.stderr:
    out.append('STDERR: %s' % r.stderr.decode('utf-8', 'replace')[:500])

io.open('tmp/out_3452.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('wrote tmp/out_3452.txt')
