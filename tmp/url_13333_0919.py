# id13333 中務裕太 写真集イベント＝25枠の飛び先が空 → 会場（県）ごとのぴあの公演ページを入れる
# eventCd は独立チェックのエージェントがぴあのまとめページ b2671194 から読んだもの
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
CD = {'長野': 2637574, '福井': 2637575, '大阪': 2633637, '兵庫': 2637576, '静岡': 2637577}
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
n = 0
for e in events:
    if e['id'] == 13333:
        for t in e['tickets']:
            p = re.search(r'（(長野|福井|大阪|兵庫|静岡) ', t['type'])
            if p and not t.get('url'):
                t['url'] = 'https://t.pia.jp/pia/event/event.do?eventCd=%d' % CD[p.group(1)]
                n += 1
print('入れた', n)
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
