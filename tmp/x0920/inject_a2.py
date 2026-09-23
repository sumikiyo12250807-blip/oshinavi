# 総ざらい2本めの新規3件（いま売っている公演・ぴあ）を新着に入れる
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
b = json.load(io.open('tmp/x0920/built_a2_new.json', encoding='utf-8-sig'))
b = b if isinstance(b, list) else b['entries']
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
nid = max(e['id'] for e in events) + 1
added = []
for x in b:
    x = dict(x)
    x['id'] = nid
    nid += 1
    x['genre'] = 'new'
    events.append(x)
    added.append(x['id'])
    print('新規 id%d %s' % (x['id'], x['name'][:40]))
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
mo = re.search(r'(NEW_ORDER\s*=\s*)\[([0-9,\s]*)\]', out)
arr = [int(v) for v in re.findall(r'\d+', mo.group(2))] + added
out = out[:mo.start()] + mo.group(1) + '[' + ', '.join(map(str, arr)) + ']' + out[mo.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
io.open('tmp/x0920/a2_new_ids.txt', 'w').write(','.join(map(str, added)))
print('NEW_ORDER', len(arr))
