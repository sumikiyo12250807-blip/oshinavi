# -*- coding: utf-8 -*-
"""id77 MeseMoa. 47都道府県ツアーを、9/22以降のe+の16公演で作り直す。
枠＝tmp/mesemoa_tickets_0922.json（エージェントがe+の個別ページ16本から組んだ）。
千秋楽＝2027/3/20 立川ステージガーデン（公式とe+の2件で一致）。会期の初日は元の8/16のまま（事実の会期）。
9/21までの公演の枠は外す（公演が終わっている）。--apply で書く。
"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
e = next(x for x in events if x['id'] == 77)
new = json.load(io.open('tmp/mesemoa_tickets_0922.json', encoding='utf-8'))

tickets, venues = [], []
for t in sorted(new, key=lambda x: x['show']):
    if t['venue'] not in venues:
        venues.append(t['venue'])
    tickets.append({k: t[k] for k in ('type', 'date', 'startDate', 'url', 'soldout', 'saleEnded',
                                       'presaleEnded', 'saleEndUnknown') if k in t})

for t in tickets:
    t['type'] = t['type'].replace('（東京都 3/20公演）', '（東京都 R9年 3/20公演）')
print('枠 %d → %d' % (len(e['tickets']), len(tickets)))
for t in tickets:
    print('  ', t['type'], '|', t.get('startDate'), t['date'], 'S' if t.get('soldout') else '', 'E' if t.get('saleEnded') else '')
e['tickets'] = tickets
e['date'] = '2027-03-20'
e['dateLabel'] = '2026年8月16日(日)〜2027年3月20日(土) 全国ツアー'
e['venue'] = '全国ツアー（' + '／'.join(venues) + '）'
e['links']['eplus'] = 'https://eplus.jp/sf/word/0000173681'
print('venue', e['venue'])

if '--apply' in sys.argv:
    nl = '\r\n' if '\r\n' in src else '\n'
    out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
    io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
    print('書き込み完了')
