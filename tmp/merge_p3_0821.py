# -*- coding: utf-8 -*-
"""新着プールの中の分裂・重複を直す（2026-08-21・検証エージェントの指摘）。

① 4932/4937/4938/4939 ＝ **同じ1試合**（2026/10/1 阪神甲子園 阪神×巨人）が
   **席種違いで4エントリに割れていた**。1エントリにまとめ、席種は tickets に展開する
   （[[feedback_tickets_all_expand]]／[[feedback_terminology_batch_split]]＝販売枠はticket、
   エントリ分割ではない）。飛び先URLは席種ごとに違うので**枠ごとにurlを持たせる**
   （[[feedback_dedup_badges_keeps_urls]]）。
② 4920【埼玉公演】＋4924【東京公演】＝「箏合奏新曲リサイタル 大川義秋 作品集VOL.1」の
   同一興行の巡演 → 1エントリへ（[[feedback_tour_consolidate]]）。
③ 4914/4915 ＝ 公演名が完全に同じ「よしもと落語 二人会」で画面上区別できない。
   出演者も日程も違う別公演なので**統合せず、名前に月を入れて区別する**
   （[[feedback_same_day_show_time_badge]]の考え方＝画面で見分けられないのが問題）。
"""
import io, re, json, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
by = {e['id']: e for e in EVENTS}

# ① 阪神×巨人 10/1 を1エントリへ（席種は枠に展開）
SEATS = [(4932, '【車椅子席】'), (4937, '【DTSボックス】'),
         (4938, '【ドコモラウンジ付き】'), (4939, '【三ツ矢サイダーボックス】')]
base = by[4932]
tickets = []
for i, label in SEATS:
    e = by[i]
    for t in e['tickets']:
        t = dict(t)
        t['type'] = t['type'].replace('一般発売', '一般発売' + label, 1) \
                             .replace('限定企画チケット発売', '限定企画チケット発売' + label, 1)
        t['url'] = (e.get('links') or {}).get('pia')
        tickets.append(t)
base['name'] = '阪神タイガース対読売ジャイアンツ 公式戦'
base['artist'] = '阪神タイガース対読売ジャイアンツ 公式戦'
base['tickets'] = tickets
base['verifiedAt'] = '2026-08-21'
print('① 4932 に統合 枠%d（4937/4938/4939 を欠番に）' % len(tickets))
for t in tickets:
    print('    -', t['type'])

# ② 箏合奏を1エントリへ
a, b = by[4920], by[4924]
a['name'] = '箏合奏新曲リサイタル 大川義秋 作品集VOL.1'
a['artist'] = '大川義秋'
a['venue'] = '全国ツアー（上戸田地域交流センターあいパル3階ホール／ヤマハホール）'
a['prefecture'] = '埼玉・東京'
a['date'] = b['date']
a['dateLabel'] = '2026年12月13日(日)〜2027年4月17日(土) 埼玉・東京'
for t in b['tickets']:
    t = dict(t)
    t['url'] = (b.get('links') or {}).get('pia')
    a['tickets'].append(t)
for t in a['tickets']:
    t.setdefault('url', (a.get('links') or {}).get('pia'))
a['verifiedAt'] = '2026-08-21'
print('② 4920 に統合 枠%d（4924 を欠番に）' % len(a['tickets']))

# ③ よしもと落語 二人会 は名前で区別
by[4914]['name'] = 'よしもと落語 二人会（10月）'
by[4915]['name'] = 'よしもと落語 二人会（11月）'
print('③ 4914/4915 の名前に月を入れた')

DROP = {4937, 4938, 4939, 4924}
KEEP = [e for e in EVENTS if e['id'] not in DROP]
assert len(KEEP) == len(EVENTS) - 4
shutil.copyfile('index.html', 'index.html.bak_0821_p3merge')
open('index.html', 'w', encoding='utf-8').write(
    h[:m.start()] + m.group(1) + json.dumps(KEEP, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
print('\n=== %d件 → %d件 ===' % (len(EVENTS), len(KEEP)))
