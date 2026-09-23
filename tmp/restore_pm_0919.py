# 昼のヒールが消した3枠を HEAD から戻す（3568 ローチケ静岡・4329 ローチケ宮城・4898 京都 2624697＝ぴあで予定枚数終了→売切印）
import io, json, re, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
head = subprocess.run(['git', 'show', 'HEAD:index.html'], capture_output=True).stdout.decode('utf-8')
H = {e['id']: e for e in json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\n\]);', head, re.S).group(1))}
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
by = {e['id']: e for e in events}
WANT = [(3568, 'l-tike.com', '一般発売（静岡 12/11公演）9/19 10:00発売', False),
        (4329, 'l-tike.com', '一般発売（宮城 11/14公演）9/19 10:00発売', False),
        (4898, 'eventCd=2624697', '一般発売（京都 12/23〜12/28公演）9/19 10:00発売', True)]
for i, key, typ, sold in WANT:
    for t in H[i]['tickets']:
        if t['type'] == typ and key in (t.get('url') or ''):
            if any(u['type'] == typ and u.get('url') == t['url'] for u in by[i]['tickets']):
                continue
            t = dict(t)
            if sold:
                t['soldout'] = True
                t['soldoutSince'] = '2026-09-19'
            by[i]['tickets'].append(t)
            print('戻した id%d %s%s' % (i, typ, ' ＋売切' if sold else ''))
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
