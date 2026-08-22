# -*- coding: utf-8 -*-
"""検証エージェントが見つけたツアーの公演落ち・表記違いを直す（2026-08-22・全部ぴあ実ページで裏取り済）。

① 4967 ミュージカル『ファインディング・ネバーランド』＝**仙台公演がまるごと抜けていた**。
   ぴあのツアーまとめページ(b2670259)に出てこないが、eventCd=2632002 に
   「東京エレクトロンホール宮城 2027/2/5〜2/7・一般発売 9/25 10:00」が生きている
   （[[feedback_pia_bundle_hides_shows]] の型そのもの）。
② 5003 プリンセス天功と楽しい仲間たち＝**静岡 掛川 9/22（受付中〜9/21 23:59）が未登録**。
   同じ演目の巡演なので1エントリにまとめる（[[feedback_tour_consolidate]]）。
   ※ぴあの表記は静岡側だけ「宝くじ文化公演 〜」の冠が付く（主催の冠。演目は同じ）。
③ 4980 ＝ 実ページの名称は「公開御礼舞台挨拶」。登録が「舞台挨拶」で落ちていたので直す。

枠ごとに飛び先URLを持たせる（[[feedback_tour_per_ticket_url]]／[[feedback_dedup_badges_keeps_urls]]）。
"""
import json
import re
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
by = {e['id']: e for e in EVENTS}

# ---------- ① 4967 仙台を足す ----------
e = by[4967]
BUNDLE = e['links']['pia']
for t in e['tickets']:
    t.setdefault('url', BUNDLE)
e['tickets'].insert(2, {
    'type': '一般発売（宮城 R9年 2/5〜2/7公演）9/25 10:00発売',
    'date': '2026-09-25', 'startDate': '2026-09-25',
    'url': 'https://t.pia.jp/pia/ticketInformation.do?eventCd=2632002&rlsCd=001'})
e['venue'] = '全国ツアー（日生劇場／東京エレクトロンホール宮城／梅田芸術劇場メインホール）'
e['prefecture'] = '東京・宮城・大阪'
e['dateLabel'] = '2027年1月8日(金)〜2027年2月15日(月) 東京・宮城・大阪'
e['verifiedAt'] = '2026-08-22'
print('① 4967 枠%d（仙台を追加・千秋楽は大阪2/15のまま %s）' % (len(e['tickets']), e['date']))

# ---------- ② 5003 静岡を足す ----------
e = by[5003]
for t in e['tickets']:
    t.setdefault('url', e['links']['pia'])
e['tickets'].insert(0, {
    'type': '一般発売（静岡 9/22公演）〜9/21 23:59', 'date': '2026-09-21',
    'url': 'https://t.pia.jp/pia/ticketInformation.do?eventCd=2618521&rlsCd=001'})
e['venue'] = '全国ツアー（掛川市生涯学習センター／尾鷲市民文化会館（せぎやまホール））'
e['prefecture'] = '静岡・三重'
e['dateLabel'] = '2026年9月22日(火)〜2026年11月3日(火) 静岡・三重'
e['verifiedAt'] = '2026-08-22'
print('② 5003 枠%d（静岡を追加・千秋楽 %s）' % (len(e['tickets']), e['date']))

# ---------- ③ 4980 名称 ----------
e = by[4980]
e['name'] = '「SEKIRO:NO DEFEAT」公開御礼舞台挨拶'
e['artist'] = e['name']
e['verifiedAt'] = '2026-08-22'
print('③ 4980 name → %s' % e['name'])

shutil.copyfile('index.html', 'index.html.bak_0822_legs')
open('index.html', 'w', encoding='utf-8').write(
    h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
print('適用した')
