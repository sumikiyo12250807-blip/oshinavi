# -*- coding: utf-8 -*-
"""id5025 水谷千重子の宴ジョインコンサート2026 の是正（ユーザーOK済み＝e+の枠を足す）。

裏取り（2026-08-28）:
  ぴあ b2667488 … 全34券種／買える枠0。公演は 福岡7/14・東京8/27・山形8/30・大阪9/7-9/8・愛知9/19・広島11/1。
                  「予定枚数終了」は 愛知9/19 一般発売の1券種のみ、他は販売終了/抽選受付終了。
  e+ 0748580001 … 大阪9/7・大阪9/8・愛知9/19 の3券種が「予定枚数終了」（受付中の枠は 0/5・0/5・0/3）。
  🚨検索一覧の「一般発売」は券種名であって販売中ではない＝個別 /sf/detail/ で裏取りした。

直すこと:
  1. date 2026-08-27 → 2026-11-01（千秋楽＝広島国際会議場フェニックスホール）
  2. venue/dateLabel/prefecture をツアー表記へ
  3. 予定枚数終了の4枠を追加（e+3＋ぴあ1）
  4. 既にある山形8/30の枠は「販売終了」バッジで残す（feedback_saleended_vs_soldout）
"""
import io, re, json, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
PATH = 'index.html'
src = io.open(PATH, encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in src[:4000] else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
E = json.loads(m.group(2))
e = next(x for x in E if x['id'] == 5025)
assert e['date'] == '2026-08-27', e['date']

e['date'] = '2026-11-01'
e['venue'] = '全国ツアー（福岡市民ホール 大ホール／東京ガーデンシアター／やまぎん県民ホール／フェスティバルホール／Niterra日本特殊陶業市民会館 フォレストホール／広島国際会議場フェニックスホール）'
e['prefecture'] = '全国'
e['dateLabel'] = '2026年11月1日(日) 広島 広島国際会議場フェニックスホール'
e['links']['eplus'] = 'https://eplus.jp/sf/detail/0748580001-P0030120P021002'

for t in e['tickets']:
    if t['type'].startswith('一般発売（山形'):
        t['soldout'] = True
        t['saleEnded'] = True
        t['saleEndedSince'] = TODAY

add = [
    {"type": "一般発売（大阪 9/7公演）〜9/4 18:00", "date": "2026-09-04",
     "url": "https://eplus.jp/sf/detail/0748580001-P0030120P021002", "soldout": True, "soldoutSince": TODAY},
    {"type": "一般発売（大阪 9/8公演）〜9/5 18:00", "date": "2026-09-05",
     "url": "https://eplus.jp/sf/detail/0748580001-P0030120P021001", "soldout": True, "soldoutSince": TODAY},
    {"type": "先着先行（愛知 9/19公演）〜9/10 18:00", "date": "2026-09-10",
     "url": "https://eplus.jp/sf/detail/0748580001-P0030123P021002", "soldout": True, "soldoutSince": TODAY},
    {"type": "一般発売（愛知 9/19公演）", "date": "2026-09-19",
     "url": "https://t.pia.jp/pia/ticketInformation.do?eventCd=2617910&rlsCd=001", "soldout": True, "soldoutSince": TODAY},
]
have = {t.get('url') for t in e['tickets']}
for a in add:
    if a['url'] not in have:
        e['tickets'].append(a)

print('date =', e['date'], '/ 枠', len(e['tickets']))
for t in e['tickets']:
    print('  -', t['type'], '| date=', t['date'], '| soldout=', t.get('soldout'), '| saleEnded=', t.get('saleEnded'))
io.open(PATH, 'w', encoding='utf-8', newline='').write(
    src[:m.start(2)] + json.dumps(E, ensure_ascii=False, indent=2).replace('\n', nl) + src[m.end(2):])
print('書き戻した')
