"""4307 レッドイーグルス北海道＝取り直し（tmp/heal_ids.json）の8枠にそっくり置き換える。
元の2枠（一般発売(WEB/紙|電子)（北海道 9/26〜9/27公演））は券種名が「WEB/紙チケット」に変わっただけで取り直しに含まれる＝足し算だと二重になるため。"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
built = {o['id']: o for o in json.load(io.open('tmp/heal_ids.json', encoding='utf-8'))}
src = io.open('index.html', encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in src else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
for e in events:
    if e['id'] == 4307:
        old = [t['type'] for t in e['tickets']]
        new = built[4307]['tickets']
        for o in old:
            k = o.replace('(WEB/紙)', '(WEB/紙チケット)').replace('(WEB/電子)', '(WEB/電子チケット)')
            assert any(t['type'] == k for t in new), o
        e['tickets'] = new
        print('4307 枠 %d → %d' % (len(old), len(new)))
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
