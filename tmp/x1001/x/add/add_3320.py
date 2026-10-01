# -*- coding: utf-8 -*-
# 3320 Plastic Tree に、川崎12/27公演の 10/2 12:00〜10/6 の先行（ぴあ発売前一覧で抜けていた）を足す＝ぴあ実ページから組んだ枠そのまま
import io, json, re
root = 'C:/Users/user/oshinavi/'
src = io.open(root + 'index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[)', src)
st = m.start(1)
E, end = json.JSONDecoder().raw_decode(src, st)
b = next(x for x in json.load(io.open(root + 'tmp/x1001/x/add/built.json', encoding='utf-8')) if x['id'] == 3320)
t = dict(next(x for x in b['tickets'] if x.get('startDate') == '2026-10-02'))
t['url'] = 'https://t.pia.jp/pia/event/event.do?eventCd=2634573'
e = next(x for x in E if x['id'] == 3320)
assert not any(x.get('startDate') == '2026-10-02' for x in e['tickets'])
e['tickets'].append(t)
body = '[\n' + ',\n'.join(json.dumps(x, ensure_ascii=False, separators=(',', ':')) for x in E) + '\n]'
io.open(root + 'index.html', 'wb').write((src[:st] + body.replace('\n', '\r\n') + src[end:]).encode('utf-8'))
print('足した', t)
