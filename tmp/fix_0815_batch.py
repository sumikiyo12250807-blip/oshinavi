# -*- coding: utf-8 -*-
"""2026-08-15 朝の修正まとめ（すべてe+/ぴあ実ページで裏取り済み）。
  3167 締切延長  〜8/15 18:00 → 〜8/18 12:00（e+ 4549640001-P0030001P02100{1,2} 実ページ）
  3038 予定枚数終了＋当日券枠追加（e+ 4500660001-P0030001P021001 実ページ）
  3743 Uru 千秋楽を9/24へ・兵庫を含むツアー形に（ぴあ b2665148 実ページ）
  2265 原田知世 千秋楽を8/31へ・サントリーホールを会場に追加（ぴあ b2667138 実ページ）
  python tmp/fix_0815_batch.py [--apply]
"""
import re, json, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
APPLY = '--apply' in sys.argv
WD = '月火水木金土日'


def jp(d):
    y, m, dd = (int(x) for x in d.split('-'))
    return '%d年%d月%d日(%s)' % (y, m, dd, WD[datetime.date(y, m, dd).weekday()])


h = open('index.html', encoding='utf-8').read()
mm = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(mm.group(2))
byid = {e['id']: e for e in EVENTS}
log = []

# --- 3167 締切延長 ---
e = byid[3167]
for t in e['tickets']:
    if t.get('date') == '2026-08-15':
        t['type'] = t['type'].replace('〜8/15 18:00', '〜8/18 12:00')
        t['date'] = '2026-08-18'
        log.append('3167 %s' % t['type'])

# --- 3038 予定枚数終了＋当日券 ---
e = byid[3038]
t0 = e['tickets'][0]
t0['soldout'] = True
t0.setdefault('soldoutSince', TODAY)
log.append('3038 予定枚数終了: %s' % t0['type'])
if not any('当日券' in (t.get('type') or '') for t in e['tickets']):
    e['tickets'].append({
        'type': '一般発売＜当日券価格＞（東京都 10/13公演）10/13 0:00発売',
        'date': '2026-10-13',
        'url': 'https://eplus.jp/sf/detail/4500660001-P0030001P021001',
        'startDate': '2026-10-13',
    })
    log.append('3038 当日券枠を追加')

# --- 3743 Uru ---
e = byid[3743]
e['date'] = '2026-09-24'
e['dateLabel'] = '%s〜%s 全国ツアー' % (jp('2026-09-03'), jp('2026-09-24'))
e['venue'] = '全国ツアー（昭和女子大学 人見記念講堂／神戸国際会館こくさいホール）'
e['prefecture'] = '全国'
log.append('3743 %s / %s' % (e['date'], e['dateLabel']))

# --- 2265 原田知世 ---
e = byid[2265]
e['date'] = '2026-08-31'
e['dateLabel'] = '%s〜%s 全国ツアー' % (jp('2026-07-10'), jp('2026-08-31'))
if 'サントリーホール' not in e['venue']:
    e['venue'] = e['venue'].rstrip('）') + '／サントリーホール 大ホール）'
log.append('2265 %s / %s' % (e['date'], e['venue']))

print('\n'.join(log))
if APPLY:
    bak = 'index.html.bak_%s_fixbatch' % datetime.date.today().strftime('%m%d')
    open(bak, 'w', encoding='utf-8').write(h)
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open('index.html', 'w', encoding='utf-8').write(h[:mm.start()] + mm.group(1) + new_arr + mm.group(3) + h[mm.end():])
    print('\n適用しました (backup: %s)' % bak)
