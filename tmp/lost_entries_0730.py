# -*- coding: utf-8 -*-
"""git HEAD の index.html と現行を比較し、消えた/増えたエントリidを洗い出す"""
import io, json, re, subprocess

def parse(raw):
    m = re.search(r'const\s+EVENTS\s*=\s*\[', raw)
    s = raw.index('[', m.start())
    depth = 0
    for i in range(s, len(raw)):
        if raw[i] == '[':
            depth += 1
        elif raw[i] == ']':
            depth -= 1
            if depth == 0:
                e = i + 1
                break
    return json.loads(raw[s:e])

cur = parse(io.open('index.html', encoding='utf-8', newline='').read())
old = parse(subprocess.run(['git', 'show', 'HEAD:index.html'],
                           capture_output=True).stdout.decode('utf-8', 'replace'))

curmap = {ev['id']: ev for ev in cur}
oldmap = {ev['id']: ev for ev in old}
lost = sorted(set(oldmap) - set(curmap))
added = sorted(set(curmap) - set(oldmap))

out = []
out.append('git HEAD %d件 → 現行 %d件' % (len(old), len(cur)))
out.append('■消えたエントリ %d件' % len(lost))
for i in lost:
    ev = oldmap[i]
    out.append('  id=%s %s / %s @ %s (%s) genre=%s' % (
        i, ev.get('artist'), ev.get('name'), ev.get('venue'), ev.get('date'), ev.get('genre')))
    for t in ev.get('tickets', []):
        out.append('      枠: %s | date=%s' % (t.get('type'), t.get('date')))
    lk = ev.get('links') or {}
    out.append('      links: %s' % json.dumps({k: v for k, v in lk.items() if v}, ensure_ascii=False))
out.append('■増えたエントリ %d件: %s' % (len(added), added))

io.open('tmp/out_lost_0730.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('lost=%d added=%d → tmp/out_lost_0730.txt' % (len(lost), len(added)))
