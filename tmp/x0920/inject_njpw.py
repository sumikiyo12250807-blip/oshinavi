# 新日本プロレス 神奈川2大会（明日9/20 10:00一般発売・総ざらいの2本めで発見）を入れる。ぴあのジャンル＝スポーツ（既存の新日本も全部 sports）
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
b = json.load(io.open('tmp/x0920/built_njpw.json', encoding='utf-8-sig'))
b = b if isinstance(b, list) else b['entries']
NAME = {90201: ('新日本プロレス<藤沢大会>', 'https://t.pia.jp/pia/event/event.do?eventCd=2633600'),
        90202: ('新日本プロレス<横浜大会>', 'https://t.pia.jp/pia/event/event.do?eventCd=2633661')}
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
nid = max(e['id'] for e in events) + 1
for x in b:
    x = dict(x)
    name, url = NAME[x['id']]
    x['id'] = nid
    nid += 1
    x['name'] = name
    x['genre'] = 'sports'
    for t in x['tickets']:
        t.setdefault('url', url)
        if not t.get('url'):
            t['url'] = url
    events.append(x)
    print('入れた id%d %s' % (x['id'], name))
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
