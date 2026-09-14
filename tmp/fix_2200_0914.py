# -*- coding: utf-8 -*-
"""push前の照合（--new・21:33〜）で出た取りこぼし4件と、単独でも0枠だった2件を、ぴあの生の行（tmp/raw_rows_2133_0914.md）どおりに直す。
・8391 新春歌謡フェスティバル in いなべ＝近日抽選受付（9/21 11:00〜9/30 23:59）が登録に無い＝足す
     券種名と日付は組み立て道具と同じ関数（kenshu・parse_when_row・mdbadge）で作る＝ビルドと同じ書き方
・8654 三遊亭白鳥 柳家三三＝締切が 9/17 → 9/19 23:59 に延びた
・8705 ゾンビフェス＝締切が 9/16 → 9/17 23:59 に延びた
・9707 しいきアルゲリッチハウス＝12/5 の公演（〜12/4 23:59）が登録に無い＝足す（登録の 12/6 は別のマスタークラス）
・9805 榛葉樹人&今井俊輔・8776 アジア競技大会ソフトテニス＝予定枚数終了＝売り切れの印（消さない）
使い方: python tmp/fix_2200_0914.py [--apply]
"""
import datetime
import io
import json
import re
import sys

sys.path.insert(0, 'tools')
import build_pia_entries as B

sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
by = {e['id']: e for e in events}


def tk(i, ty):
    hit = [t for t in by[i]['tickets'] if t.get('type') == ty]
    assert len(hit) == 1, 'id%s の枠が1つに決まらない（%d）: %s' % (i, len(hit), ty)
    return hit[0]


# 8391
e = by[8391]
row = {'state': '発売前', 'stt': '近日抽選受付', 'when': '2026/9/21(月・祝) 11:00 ～ 2026/9/30(水) 23:59',
       'title': '新春歌謡フェスティバル in いなべ〔三重〕', 'perfdate': '2027-01-30', 'perf_end': '2027-01-30',
       'venue': 'いなべ市北勢市民会館 さくらホール', 'prefs': ['三重'], 'url': ''}
suf, iso, sd = B.parse_when_row(row)
ks = B.drop_labels_in_name(B.kenshu(row['title']), e.get('artist'))
t = {'type': B.norm_fw('%s（三重 %s公演）%s' % (ks, B.mdbadge('2027-01-30', '2027-01-30'), suf)), 'date': iso}
if sd:
    t['startDate'] = sd
assert t['type'] not in {x['type'] for x in e['tickets']}
e['tickets'] = sorted(e['tickets'] + [t], key=lambda x: x['date'])
# 8654
t = tk(8654, '一般発売（東京 9/24公演）〜9/17 23:59')
t['type'], t['date'] = '一般発売（東京 9/24公演）〜9/19 23:59', '2026-09-19'
# 8705
t = tk(8705, '一般発売（東京 9/18〜9/19公演）〜9/16 23:59')
t['type'], t['date'] = '一般発売（東京 9/18〜9/19公演）〜9/17 23:59', '2026-09-17'
# 9707
e = by[9707]
add = {'type': '一般発売（大分 12/5公演）〜12/4 23:59', 'date': '2026-12-04'}
assert add['type'] not in {x['type'] for x in e['tickets']}
e['tickets'] = sorted(e['tickets'] + [add], key=lambda x: x['date'])
# 9805・8776
for i, ty in [(9805, '一般販売（東京 9/16公演）〜9/15 23:59'), (8776, '一般発売（愛知 9/18〜9/23公演）〜9/23 9:00')]:
    t = tk(i, ty)
    t['soldout'] = True
    t['soldoutSince'] = TODAY
for i in (8391, 8654, 8705, 9707, 9805, 8776):
    x = by[i]
    print('## id%s %s ｜date %s' % (i, x['name'], x['date']))
    for t in x['tickets']:
        print('   %s ｜締切 %s｜発売 %s%s' % (t['type'], t['date'], t.get('startDate') or '-', '｜売り切れ' if t.get('soldout') else ''))
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('書き込み完了')
