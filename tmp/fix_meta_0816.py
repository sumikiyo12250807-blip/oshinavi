# -*- coding: utf-8 -*-
"""id=300 / 3834 のエントリ見出し情報（date/dateLabel/venue/prefecture）をぴあ実ページの再導出に合わせて直す。
ticketsは触らない（ヒール適用済み）。書き戻しは heal_stale_deadlines.py と同じ方式＝
open(...,'w',encoding='utf-8') のテキストモードでCRLFを維持する。
"""
import re, json, sys, os, shutil
sys.stdout.reconfigure(encoding='utf-8')

FIX = {
    300: {
        # ぴあ b2665822 の現存枠は愛知(御園座 8/22-23)・山梨(YCC 8/29-30)。東京・大阪は終了済み。
        "date": "2026-08-30",
        "dateLabel": "2026年8月22日(土)〜2026年8月30日(日) 愛知・山梨",
        "venue": "全国ツアー（御園座／YCC県民文化ホール 大ホール）",
        "prefecture": "愛知・山梨",
    },
    3834: {
        # 実会場公演(9/27 なかのZERO)は完売/終了。生きている枠は動画配信(〜R9年1/31)のみ。
        # dateが9/27のままだと配信枠が買えるのに画面から消えるのでdateを配信最終日に。
        "date": "2027-01-31",
        "dateLabel": "2026年9月27日(日) 東京 なかのZERO 大ホール ／ 動画配信 〜2027年1月31日(日)",
        "venue": "なかのZERO 大ホール／PIA LIVE STREAM（動画配信）",
    },
}

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

changed = 0
for e in EVENTS:
    f = FIX.get(e.get('id'))
    if not f:
        continue
    for k, v in f.items():
        if e.get(k) != v:
            print("id=%s %-11s %s → %s" % (e['id'], k, e.get(k), v))
            e[k] = v
            changed += 1

if not changed:
    print("変更なし"); sys.exit(0)

bak = 'index.html.bak_0816_meta'
if not os.path.exists(bak):
    open(bak, 'w', encoding='utf-8').write(h)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print("=== %d項目 適用 (backup: %s) ===" % (changed, bak))
