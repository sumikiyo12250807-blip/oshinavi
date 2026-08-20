# -*- coding: utf-8 -*-
"""Hyogoクリスマス・ジャズ・フェスティバル2026 の6件(id4178-4183)を1エントリに統合。
残すのは最小id 4178。4179-4183 は削除し NEW_ORDER からも外す（欠番運用・id振り直しはしない）。
バッジには出演者を残して枠を区別できるようにする（同じ文字列のバッジを作らない）。
index.html は CRLF 維持（memory: feedback_index_html_crlf_preserve）。
"""
import re, json, io, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

KEEP = 4178
DROP = [4179, 4180, 4181, 4182, 4183]

# 公演日順（12/11→12/24）。バッジ用の出演者ラベルは実データの名前から手で短縮した。
ROWS = [
    ("2026-12-11", "大西順子",              "神戸女学院小ホール", "2628813"),
    ("2026-12-12", "4TRP.Legends",         "阪急 中ホール",     "2629498"),
    ("2026-12-15", "オールスター・ジャムセッション", "阪急 中ホール",     "2629547"),
    ("2026-12-16", "小曽根 真",             "KOBELCO大ホール",   "2628881"),
    ("2026-12-18", "北村英治クインテット",     "神戸女学院小ホール", "2629076"),
    ("2026-12-24", "アロージャズオーケストラ",  "KOBELCO大ホール",   "2629081"),
]
URL = "https://t.pia.jp/pia/event/event.do?eventCd=%s"

h = io.open('index.html', encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

by_id = {e['id']: e for e in EVENTS}
for i in [KEEP] + DROP:
    assert i in by_id, 'id%d が無い' % i

keep = by_id[KEEP]
keep['name'] = 'Hyogoクリスマス・ジャズ・フェスティバル2026'
keep['artist'] = '小曽根 真／大西順子／北村英治／類家心平／広瀬未来／アロージャズオーケストラ ほか'
keep['venue'] = '兵庫県立芸術文化センター（KOBELCO大ホール／阪急 中ホール／神戸女学院小ホール）'
keep['prefecture'] = '兵庫'
keep['date'] = ROWS[-1][0]
keep['dateLabel'] = '2026年12月11日(金)〜2026年12月24日(木) 兵庫 兵庫県立芸術文化センター'
keep['tickets'] = [{
    'type': '一般発売 %s（兵庫 %d/%d公演）9/6 10:00発売' % (
        who, int(d[5:7]), int(d[8:10])),
    'date': '2026-09-06',
    'startDate': '2026-09-06',
    'url': URL % cd,
} for (d, who, hall, cd) in ROWS]
keep['links'] = dict(keep.get('links') or {})
keep['links']['pia'] = URL % ROWS[0][3]
keep['verifiedAt'] = '2026-08-13'

EVENTS = [e for e in EVENTS if e['id'] not in DROP]

# NEW_ORDER から消したidを外す（配列にだけ残ると並び順の穴になる）
mo = re.search(r'(NEW_ORDER\s*=\s*)\[([0-9,\s]*)\]', h)
cur = [int(x) for x in re.findall(r'\d+', mo.group(2))]
new_order = [i for i in cur if i not in DROP]
h2 = re.sub(r'(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]',
            r'\g<1>[' + ', '.join(str(i) for i in new_order) + ']', h, count=1)
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h2, re.S)

print('統合後 tickets=%d / 総%d件 / NEW_ORDER %d→%d' % (
    len(keep['tickets']), len(EVENTS), len(cur), len(new_order)))
for t in keep['tickets']:
    print('  枠|', t['type'])

bak = 'index.html.bak_%s_hyogo' % datetime.date.today().strftime('%m%d')
io.open(bak, 'w', encoding='utf-8', newline='').write(h)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
io.open('index.html', 'w', encoding='utf-8', newline='').write(
    h2[:m.start()] + m.group(1) + new_arr + m.group(3) + h2[m.end():])
print('適用完了 (backup %s)' % bak)
