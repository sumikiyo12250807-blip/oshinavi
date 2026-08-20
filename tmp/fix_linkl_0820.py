# -*- coding: utf-8 -*-
"""4656 LINKL PLANET を作り直す。

見つかった問題（2026-08-20・pia_deadlink_scan の DEAD 1件から芋づるで発覚）:
  ・ぴあの eventCd=2633279 が消えている（3430と同じ「発売前なのにページが作り直される」型）
  ・実体は **2nd Live Tour「CONNECT PARTS」＝3会場6公演**
      東京 10/17(土) 昼13:30・夜17:30 duo MUSIC EXCHANGE
      愛知 11/7(土) 昼13:30・夜17:30 NAGOYA JAMMIN'
      大阪 11/8(日) 昼13:00・夜17:00 ESAKA MUSE
  ・**6公演すべての「先着先行」が受付中（2026/8/1 12:00〜8/23 23:59）**なのに登録に1枠も無い
  ・登録にあったのは「愛知11/7・8/29 10:00発売」の1枠だけ（ぴあ由来）

出典＝e+ /sf/detail/3739940001（tools/eplus_detail.py で機械抽出）
"""
import io, re, json, sys, urllib.request, shutil
sys.stdout.reconfigure(encoding='utf-8')

URL = 'https://eplus.jp/sf/detail/3739940001'
req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req, timeout=60).read().decode('utf-8', 'replace')

# 公演ごとの個別URL（/sf/detail/3739940001-P00300xxP0210xx）を拾う
urls = sorted(set(re.findall(r'/sf/detail/3739940001-P[0-9A-Za-z]+', html)))
print('e+ の個別URL候補 %d件' % len(urls))
for u in urls[:12]:
    print('   https://eplus.jp' + u)

SHOWS = [
    ('東京', '10/17 13:30', '2026-10-17'),
    ('東京', '10/17 17:30', '2026-10-17'),
    ('愛知', '11/7 13:30', '2026-11-07'),
    ('愛知', '11/7 17:30', '2026-11-07'),
    ('大阪', '11/8 13:00', '2026-11-08'),
    ('大阪', '11/8 17:00', '2026-11-08'),
]
tickets = []
for i, (pref, when, _d) in enumerate(SHOWS):
    t = {
        'type': '先着先行（%s %s公演）〜8/23 23:59' % (pref, when),
        'date': '2026-08-23',
        'url': ('https://eplus.jp' + urls[i]) if i < len(urls) else URL,
    }
    tickets.append(t)
# ぴあの一般発売（8/29 10:00）は発売前なので残す。ただしぴあURLは死んでいるので付けない
tickets.append({
    'type': '一般発売（愛知 11/7公演）8/29 10:00発売',
    'date': '2026-08-29',
    'startDate': '2026-08-29',
})

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
n = 0
for e in EVENTS:
    if e['id'] != 4656:
        continue
    print('\nbefore: 枠%d / venue=%s / date=%s' % (len(e.get('tickets') or []), e.get('venue'), e.get('date')))
    e['artist'] = 'LINKL PLANET'
    e['name'] = 'LINKL PLANET'
    e['venue'] = "全国ツアー（duo MUSIC EXCHANGE／NAGOYA JAMMIN'／ESAKA MUSE）"
    e['prefecture'] = '東京・愛知・大阪'
    e['date'] = '2026-11-08'
    e['dateLabel'] = "2026年10月17日(土)〜2026年11月8日(日) 東京・愛知・大阪"
    e['tickets'] = tickets
    links = e.get('links') or {}
    links['pia'] = None          # ぴあのページが消えている
    links['eplus'] = URL
    e['links'] = links
    e['verifiedAt'] = '2026-08-20'
    n += 1
    print('after : 枠%d / venue=%s / date=%s' % (len(tickets), e['venue'], e['date']))
    for t in tickets:
        print('   -', t['type'], '|', (t.get('url') or 'ぴあ発売前')[:64])

assert n == 1
shutil.copyfile('index.html', 'index.html.bak_0820_linkl')
open('index.html', 'w', encoding='utf-8').write(
    h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
print('\n=== 更新 ===')
