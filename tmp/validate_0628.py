# -*- coding: utf-8 -*-
"""新着50件(id1494-1543)のゼロエラー自己チェック。reconcileの枠数照合の先＝
日付cap/全角残り/席種重複バッジ/県venue整合/発売前startDate/空カッコ/name質 を機械検査。"""
import re, json, io, sys, unicodedata
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
h = open('index.html', encoding='utf-8').read()
m = re.search(r'const EVENTS = (\[.*?\]);', h, re.S); arr = json.loads(m.group(1))
new = [e for e in arr if 1494 <= e['id'] <= 1543]
PREFS = '北海道|青森|岩手|宮城|秋田|山形|福島|茨城|栃木|群馬|埼玉|千葉|東京|神奈川|新潟|富山|石川|福井|山梨|長野|岐阜|静岡|愛知|三重|滋賀|京都|大阪|兵庫|奈良|和歌山|鳥取|島根|岡山|広島|山口|徳島|香川|愛媛|高知|福岡|佐賀|長崎|熊本|大分|宮崎|鹿児島|沖縄'
issues = []
def add(eid, tag, msg): issues.append((eid, tag, msg))

for e in new:
    eid = e['id']; perf = e.get('date'); pref = e.get('prefecture'); ven = e.get('venue','')
    # 全角ローマ字/数字残り(type/name/venue)
    for field in ('name','venue','dateLabel'):
        v = e.get(field) or ''
        if re.search(r'[Ａ-Ｚａ-ｚ０-９]', v):
            add(eid, '全角残り', f"{field}='{v[:30]}'")
    # 空カッコ
    if '（）' in ven or '()' in ven: add(eid,'空カッコ', f"venue='{ven}'")
    # バッジ重複(同一type文字列)
    types = [t['type'] for t in e['tickets']]
    dup = [t for t in set(types) if types.count(t) > 1]
    if dup: add(eid,'バッジ重複', f"{dup}")
    # 県とvenue/pref整合: prefが単一県なのにdateLabelに別県? ざっくり pref が全国でなければtypeの県を確認
    seen_prefs = set()
    for t in e['tickets']:
        for p in re.findall(r'（([^）]*?)\s*\d', t['type']):
            for pp in re.findall(PREFS, p): seen_prefs.add(pp)
    if pref not in ('全国', None) and seen_prefs and pref not in seen_prefs:
        add(eid,'県不整合', f"pref={pref} but ticket県={seen_prefs}")
    # 各ticket: 日付cap(受付終了>公演日?) / 発売前startDate / 全角type
    for t in e['tickets']:
        ty = t['type']; d = t.get('date'); sd = t.get('startDate'); sus = t.get('saleUntilSoldOut')
        if re.search(r'[Ａ-Ｚａ-ｚ０-９]', ty): add(eid,'全角type', ty[:36])
        # 公演日(type内 M/D) 抽出して cap 確認
        mds = re.findall(r'(\d{1,2})/(\d{1,2})公演', ty)
        if d and mds:
            # 最遅公演日
            yr = int(perf[:4]) if perf else 2026
            perfdays = []
            for mm,dd in mds:
                mm,dd=int(mm),int(dd)
                y = yr if mm>=6 else yr+ (1 if int(perf[5:7])>mm else 0)
                perfdays.append(f"{y}-{mm:02d}-{dd:02d}")
            latest = max(perfdays)
            if d > latest:
                add(eid,'cap逸脱', f"締切{d} > 公演{latest} | {ty[:30]}")
        # 発売前なのにsaleUntilSoldOut
        if sd and sus: add(eid,'発売前SUS', ty[:30])
        # 発売前はstartDate===date のはず
        if sd and d and sd != d: add(eid,'発売前date不一致', f"sd{sd}!=d{d} {ty[:24]}")
        # type末尾フォーマット(〜M/D or M/D発売)
        if not re.search(r'(〜\d{1,2}/\d{1,2}|\d{1,2}/\d{1,2}.*発売|予定枚数|当日)', ty):
            add(eid,'type末尾不明', ty[:36])
    # name=venue丸かぶり(イベント名欠如)疑い
    if e.get('name')==e.get('artist') and len(e.get('name',''))<3:
        add(eid,'name短すぎ', e.get('name'))

print(f"=== 新着50件 自己チェック / 検出 {len(issues)}件 ===")
from collections import defaultdict
bytag=defaultdict(list)
for eid,tag,msg in issues: bytag[tag].append((eid,msg))
for tag,lst in sorted(bytag.items()):
    print(f"\n[{tag}] {len(lst)}件")
    for eid,msg in lst: print(f"   id{eid}: {msg}")
if not issues: print("✅ 機械検査クリア（全角/空カッコ/バッジ重複/県整合/cap/発売前/type末尾 全てOK）")
