# id2992 カイブツはささやく 東京の一般発売＝ぴあで「予定枚数終了」→ 売り切れの印（消さない）
import io, json, re
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
for e in events:
    if e['id'] == 2992:
        for t in e['tickets']:
            if t['type'].startswith('一般発売（東京 10/11〜12/20公演）'):
                t['soldout'] = True
                t['soldoutSince'] = '2026-09-19'
                print('marked', t['type'])
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
