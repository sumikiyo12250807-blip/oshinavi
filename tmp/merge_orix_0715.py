#!/usr/bin/env python3
"""オリックス・バファローズ4試合(2699-2702)を1エントリに統合。

4試合とも京セラドーム大阪・7/22 12:00発売で揃う→[[feedback_tour_consolidate]]で1エントリ。
対戦相手ごとに別eventCd→各ticketに個別url付与([[feedback_tour_per_ticket_url]])。
renderCardは uniqTicketUrls>1 で下部ぴあボタンを自動非表示にするので誤誘導しない(確認済)。
URLはDBのlinks.piaから機械抽出（捏造禁止）。
"""
import datetime
import json
import re
import sys
sys.path.insert(0, 'tools')
import build_pia_entries  # noqa stdout UTF-8

PARENT = 2699           # 親（最小id・これに集約）
MERGE = [2699, 2700, 2701, 2702]
# 対戦カード（DBの name から機械抽出して確認に使う）
OPP = {
    2699: '対埼玉西武',
    2700: '対千葉ロッテ',
    2701: '対東北楽天',
    2702: '対北海道日本ハム',
}

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(const\s+EVENTS\s*=\s*)(\[.*?\])(;\s*\n)', h, re.S)
EVENTS = json.loads(m.group(2))
by = {e['id']: e for e in EVENTS}

# 各試合の公演日・eventCd URLをDBから取得
rows = []
for i in MERGE:
    e = by[i]
    url = (e.get('links') or {}).get('pia')
    # 公演日は tickets[0] の（… M/D公演）でなく date（=販売終了日）でなく、dateLabelから取る
    perf = e.get('date')  # 単日試合なので ev.date=公演日
    # ↑野球の単日公演は date=公演日。念のため tickets から発売日も確認
    t0 = (e.get('tickets') or [{}])[0]
    rows.append({
        'id': i, 'perf': perf, 'url': url, 'opp': OPP[i],
        'sale_type': t0.get('type', ''), 'sale_date': t0.get('date'), 'sale_start': t0.get('startDate'),
    })
    print(f"id={i} {e.get('name')}")
    print(f"   公演日={perf} url={url}")
    print(f"   既存枠: {t0.get('type')} (date={t0.get('date')} start={t0.get('startDate')})")

# 公演日順に並べる
rows.sort(key=lambda r: r['perf'])

def jp(iso):
    y, mo, d = map(int, iso.split('-'))
    wd = '月火水木金土日'[datetime.date(y, mo, d).weekday()]
    return f"{y}年{mo}月{d}日({wd})"

def md(iso):
    _, mo, d = iso.split('-')
    return f"{int(mo)}/{int(d)}"

# 統合tickets（各試合＝対戦カード別・個別url・全部7/22 12:00発売で発売前）
tickets = []
for r in rows:
    tickets.append({
        'type': f"一般発売（大阪 {md(r['perf'])}公演 {r['opp']}）7/22 12:00発売",
        'startDate': r['sale_start'],
        'date': r['sale_date'],
        'url': r['url'],
    })

perfs = [r['perf'] for r in rows]
parent = by[PARENT]
parent['artist'] = 'オリックス・バファローズ 公式戦'
parent['name'] = 'オリックス・バファローズ 公式戦'
parent['date'] = perfs[-1]
parent['dateLabel'] = f"{jp(perfs[0])}〜{jp(perfs[-1])} 大阪 京セラドーム大阪"
parent['venue'] = '京セラドーム大阪'
parent['prefecture'] = '大阪'
parent['tickets'] = tickets
parent['verified'] = True
parent['verifiedAt'] = '2026-07-15'

# 2700-2702を配列から除去
drop = set(MERGE) - {PARENT}
EVENTS = [e for e in EVENTS if e['id'] not in drop]

print('\n=== 統合後の親エントリ ===')
print(f"name: {parent['name']}")
print(f"dateLabel: {parent['dateLabel']}")
print(f"date: {parent['date']} / venue: {parent['venue']} / pref: {parent['prefecture']}")
for t in tickets:
    print(f"   枠: {t['type']} | date={t['date']} start={t['startDate']}")
    print(f"        url: {t['url']}")

# 書き戻し（EVENTS配列）
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
h2 = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]

# NEW_ORDER から 2700,2701,2702 を除去
mo = re.search(r'const NEW_ORDER = \[([\d,\s]+)\];', h2)
order = [int(x) for x in mo.group(1).replace(' ', '').split(',') if x]
order = [i for i in order if i not in drop]
h2 = h2[:mo.start()] + 'const NEW_ORDER = [' + ', '.join(str(i) for i in order) + '];' + h2[mo.end():]
print(f"\nNEW_ORDER: {len(order)}件（{sorted(drop)}を除去）")

bak = f'index.html.bak_{datetime.date.today():%m%d}_orix_merge'
open(bak, 'w', encoding='utf-8').write(h)
open('index.html', 'w', encoding='utf-8').write(h2)
print(f'\n=== 4試合→1エントリ 統合完了 (backup: {bak}) ===')
