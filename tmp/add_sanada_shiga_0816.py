# -*- coding: utf-8 -*-
"""真田ナオキ(id775) に e+ の滋賀10/28公演を追加する。
根拠＝https://eplus.jp/sf/detail/4534120001-P0030001P021001
  タイトル「真田ナオキ コンサート2026 IN 滋賀のチケット情報(2026/10/28(水))」
  会場 栗東芸術文化会館さきら 大ホール／先着 一般発売 受付 2026/6/27 10:00〜2026/10/27(火)18:00・受付中
plan.md 宿題「真田ナオキのe+取りこぼし」の実体はこの1公演だけだった
（東京ニッショーホールはIKKO DRAMATICの公演＝別アーティスト、熊本は予定枚数終了、愛知/兵庫/大阪は登録済み）。
"""
import re, json, sys, os
sys.stdout.reconfigure(encoding='utf-8')

NEW_TICKET = {
    "type": "一般発売（滋賀 10/28公演）〜10/27 18:00",
    "date": "2026-10-27",
    "url": "https://eplus.jp/sf/detail/4534120001-P0030001P021001",
}

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

hit = False
for e in EVENTS:
    if e.get('id') != 775:
        continue
    hit = True
    if any(t.get('url') == NEW_TICKET['url'] for t in e.get('tickets') or []):
        print("既に登録済み"); sys.exit(0)
    # 枠は date 昇順を保って挿入（10/27 は大阪 11/14 の前）
    tks = e.setdefault('tickets', [])
    pos = len(tks)
    for i, t in enumerate(tks):
        if (t.get('date') or '') > NEW_TICKET['date']:
            pos = i; break
    tks.insert(pos, dict(NEW_TICKET))
    e['dateLabel'] = e['dateLabel'].replace("／11月22日(日)大阪", "／10月28日(水)滋賀／11月22日(日)大阪")
    e['venue'] = e['venue'].replace("／サンケイホールブリーゼ", "／栗東芸術文化会館さきら 大ホール／サンケイホールブリーゼ")
    e['prefecture'] = e['prefecture'].replace("・大阪", "・滋賀・大阪")
    print("枠追加:", NEW_TICKET['type'])
    print("dateLabel :", e['dateLabel'])
    print("venue     :", e['venue'])
    print("prefecture:", e['prefecture'])

if not hit:
    print("id775 が見つからない"); sys.exit(1)

bak = 'index.html.bak_0816_sanada'
if not os.path.exists(bak):
    open(bak, 'w', encoding='utf-8').write(h)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print("=== 適用 (backup: %s) ===" % bak)
