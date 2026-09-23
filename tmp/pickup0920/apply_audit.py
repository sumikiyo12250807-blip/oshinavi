# 総ざらいの組み上がり：7088 アイカツは飛び先だけ入れる／90002〜90004 は新規で新着へ
#   python tmp/pickup0920/apply_audit.py [--apply]
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
b = json.load(io.open('tmp/pickup0920/built_audit.json', encoding='utf-8-sig'))
b = b if isinstance(b, list) else b['entries']
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
by = {e['id']: e for e in events}
added = []
nid = max(by) + 1
for x in b:
    if x['id'] == 7088:
        for t in by[7088]['tickets']:
            if t.get('url'):
                continue
            hit = [u for u in x['tickets'] if u['type'] == t['type'] and u.get('url')]
            if hit:
                t['url'] = hit[0]['url']
                print('id7088 飛び先', t['type'][:40], hit[0]['url'])
        continue
    x = dict(x)
    x['id'] = nid
    nid += 1
    x['genre'] = 'new'
    events.append(x)
    added.append(x['id'])
    print('新規 id%d %s 枠%d' % (x['id'], x['name'], len(x['tickets'])))
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
mo = re.search(r'(NEW_ORDER\s*=\s*)\[([0-9,\s]*)\]', out)
arr = [int(v) for v in re.findall(r'\d+', mo.group(2))] + added
out = out[:mo.start()] + mo.group(1) + '[' + ', '.join(map(str, arr)) + ']' + out[mo.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('書き込み完了 NEW_ORDER', len(arr))
