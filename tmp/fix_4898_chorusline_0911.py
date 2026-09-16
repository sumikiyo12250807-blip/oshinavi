# -*- coding: utf-8 -*-
"""id4898 劇団四季『コーラスライン』全国ツアーに、12/17以降の公演のローチケ枠を足し、会期をツアーの事実に合わせる
（2026-09-11 ユーザー「２ＯＫ」＝ローチケ/e+の枠を足して会期を2027/1/31まで伸ばす）。

受付期間は実ブラウザでローチケの各ページを読んで確かめた（2026-09-11 夕）:
  和歌山 12/17  Lコード53133  2026/8/25 10:00〜12/14 23:59（発売中・S/A席は予定枚数終了・B席残りわずか）
  岸和田 12/19  Lコード52242  2026/10/7 10:00〜12/16 23:59（e+も同じ公演 10/7 10:00〜12/16 18:00＝締切の遅いローチケ1枠にする）
  京都 12/23〜28 Lコード54363  2026/9/19 10:00〜12/22 23:59
  大阪 12/30〜1/5 Lコード54574 2026/9/19 10:00〜12/30 23:59
  下松 1/24     Lコード63267  2026/10/25 10:00〜2027/1/21 23:59
会期の出典＝公式の全国ツアーマップ https://www.shiki.jp/applause/chorusline/special/map/
  （2026/8/1 海老名 開幕 〜 2027/1/27〜31 広島）＝[[feedback_show_true_dates_not_sellable_range]]
四季の自社販売だけの公演地（たつの・浦安・宇都宮・ひたちなか）と、どこにも出ていない四国・福山・広島は枠を足さない。
"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
ADD = [
    {"type": "一般発売（和歌山 12/17公演）〜12/14 23:59", "date": "2026-12-14",
     "url": "https://l-tike.com/order/?gLcode=53133"},
    {"type": "一般発売（大阪 12/19公演）10/7 10:00発売 〜12/16 23:59", "date": "2026-12-16", "startDate": "2026-10-07",
     "url": "https://l-tike.com/order/?gLcode=52242"},
    {"type": "一般発売（京都 12/23〜12/28公演）9/19 10:00発売 〜12/22 23:59", "date": "2026-12-22", "startDate": "2026-09-19",
     "url": "https://l-tike.com/order/?gLcode=54363"},
    {"type": "一般発売（大阪 12/30〜R9年 1/5公演）9/19 10:00発売 〜12/30 23:59", "date": "2026-12-30", "startDate": "2026-09-19",
     "url": "https://l-tike.com/order/?gLcode=54574"},
    {"type": "一般発売（山口 R9年 1/24公演）10/25 10:00発売 〜1/21 23:59", "date": "2027-01-21", "startDate": "2026-10-25",
     "url": "https://l-tike.com/order/?gLcode=63267"},
]
VENUES = ['和歌山県民文化会館 大ホール', '南海浪切ホール 大ホール', '京都劇場', 'SkyシアターMBS', 'スターピアくだまつ Kビジョンホール']
src = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
ev = json.loads(m.group(2))
for e in ev:
    if e['id'] != 4898:
        continue
    have = {t['type'] for t in e['tickets']}
    # 画面の飛び先が壊れないよう、url 空の既存枠にカードのリンクを焼き込んでから足す
    for t in e['tickets']:
        if not t.get('url'):
            t['url'] = e['links']['pia']
    for a in ADD:
        if a['type'] not in have:
            e['tickets'].append(a)
    e['date'] = '2027-01-31'
    e['dateLabel'] = '2026年8月1日(土)〜2027年1月31日(日) 全国ツアー'
    inner = re.match(r'^全国ツアー（(.*)）$', e['venue']).group(1).split('／')
    e['venue'] = '全国ツアー（%s）' % '／'.join(inner + [v for v in VENUES if v not in inner])
    print(e['dateLabel'], '|', e['date'], '| 枠', len(e['tickets']))
    print(e['venue'])
open('index.html', 'w', encoding='utf-8').write(src[:m.start()] + m.group(1) + json.dumps(ev, ensure_ascii=False, indent=2) + m.group(3) + src[m.end():])
