# 新規の組み上がりを新着に入れる（9/19夜）
#  ・駐車場予約券だけのページ（90103・90104）は入れない＝ぴあの駐車券ページはユーザー未確認（memory feedback_oshinavi_concept）
#  ・CS ファイナルステージの日程違い3件＋車イスゾーン（90105〜90108）は1エントリにまとめる（ツアー・同じ興行は1エントリ）
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
b = json.load(io.open('tmp/x0920/built_new.json', encoding='utf-8-sig'))
b = b if isinstance(b, list) else b['entries']
by = {x['id']: x for x in b}
SKIP = {90103, 90104}
CS = [90105, 90106, 90107, 90108]
cs = dict(by[90105])
cs['name'] = cs['artist'] = '2026 パーソル クライマックスシリーズ パ ファイナルステージ 福岡ソフトバンクホークス対ファーストステージ勝者'
cs['tickets'] = []
for i in CS:
    for t in by[i]['tickets']:
        t = dict(t)
        if i == 90108 and '車イス' not in t['type']:
            t['type'] = t['type'].replace('一般発売', '一般発売【車イスゾーン】', 1)
        cs['tickets'].append(t)
cs['date'] = '2026-10-20'
cs['dateLabel'] = '2026年10月14日(水)〜2026年10月20日(火) 福岡 みずほPayPayドーム福岡'
items = [x for x in b if x['id'] not in SKIP and x['id'] not in CS] + [cs]

src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
nid = max(e['id'] for e in events) + 1
added = []
for x in items:
    x = dict(x)
    x['id'] = nid
    nid += 1
    x['genre'] = 'new'
    events.append(x)
    added.append(x['id'])
    print('新規 id%d %s 枠%d' % (x['id'], x['name'][:40], len(x['tickets'])))
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
mo = re.search(r'(NEW_ORDER\s*=\s*)\[([0-9,\s]*)\]', out)
arr = [int(v) for v in re.findall(r'\d+', mo.group(2))] + added
out = out[:mo.start()] + mo.group(1) + '[' + ', '.join(map(str, arr)) + ']' + out[mo.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
io.open('tmp/x0920/new_ids.txt', 'w').write(','.join(map(str, added)))
print('書き込み完了 NEW_ORDER', len(arr))
