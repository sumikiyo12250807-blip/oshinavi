# -*- coding: utf-8 -*-
"""新着47件の再チェック（3周目）。朝と別の観点を潰す。
 A) prefecture 誤検出（会場名の命名権で他県に化ける過去バグ）
 B) 既存エントリとの重複（artist正規化・会場+公演日の一致）
 C) バッジの公演日と dateLabel/ev.date の整合
 D) 発売日が過去になっていないか（発売済みなのに「発売前」表示）
"""
import re, json, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

TODAY = datetime.date(2026, 7, 19)
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
ALL = json.loads(m.group(2))
NEW = [e for e in ALL if 2865 <= (e.get('id') or 0) <= 2914]
OLD = [e for e in ALL if not (2865 <= (e.get('id') or 0) <= 2914)]
print(f'新着{len(NEW)}件 / 既存{len(OLD)}件\n')

PREFS = ['北海道','青森','岩手','宮城','秋田','山形','福島','茨城','栃木','群馬','埼玉','千葉',
         '東京','神奈川','新潟','富山','石川','福井','山梨','長野','岐阜','静岡','愛知','三重',
         '滋賀','京都','大阪','兵庫','奈良','和歌山','鳥取','島根','岡山','広島','山口','徳島',
         '香川','愛媛','高知','福岡','佐賀','長崎','熊本','大分','宮崎','鹿児島','沖縄']
n = 0

print('--- A) 都道府県の妥当性 ---')
for e in NEW:
    p = e.get('prefecture')
    # バッジに書かれた県（＝ぴあ由来の正）を集める
    badge = set()
    for t in e.get('tickets', []):
        mm = re.search(r'（([^）]*?)\s*[\d R]', t.get('type', '') or '')
        if mm:
            for pr in PREFS:
                if pr in mm.group(1):
                    badge.add(pr)
    if not badge:
        continue
    if p == '全国':
        if len(badge) == 1:
            print(f'  ⚠️ id={e["id"]} {e.get("name")} pref=全国 だがバッジは{badge}のみ'); n += 1
    elif p not in badge:
        print(f'  ⚠️ id={e["id"]} {e.get("name")} pref={p} / バッジ={sorted(badge)}'); n += 1
print('  （指摘なしなら空）\n')

print('--- B) 既存との重複（会場＋公演日が一致）---')
key_old = {}
for e in OLD:
    key_old.setdefault((e.get('venue'), e.get('date')), []).append(e)
for e in NEW:
    hit = key_old.get((e.get('venue'), e.get('date')))
    if hit:
        for o in hit:
            print(f'  ⚠️ 新着 id={e["id"]} {e.get("name")}')
            print(f'      既存 id={o["id"]} {o.get("name")} | {o.get("venue")} {o.get("date")}'); n += 1
def na(s):
    return re.sub(r'[\s　・／/（）()【】]', '', (s or '')).lower()
old_artist = {}
for e in OLD:
    old_artist.setdefault(na(e.get('artist')), []).append(e)
for e in NEW:
    for o in old_artist.get(na(e.get('artist')), []):
        print(f'  ⚠️ artist一致 新着 id={e["id"]} {e.get("artist")} ⇔ 既存 id={o["id"]} {o.get("name")} ({o.get("date")})'); n += 1
print('  （指摘なしなら空）\n')

print('--- C) バッジ公演日 vs ev.date/dateLabel ---')
for e in NEW:
    ev = e.get('date')
    for t in e.get('tickets', []):
        ty = t.get('type', '')
        # 「M/D公演」「M/D〜M/D公演」「R9年 M/D公演」を拾う
        days = re.findall(r'(?:R9年\s*)?(\d{1,2})/(\d{1,2})(?=[公〜～])', ty)
        if not days:
            continue
        last = days[-1]
        md = f'{int(last[0]):02d}-{int(last[1]):02d}'
        if not ev.endswith(md):
            print(f'  ⚠️ id={e["id"]} {e.get("name")}')
            print(f'      ev.date={ev} / バッジ末尾の公演日={md} | {ty}'); n += 1
print('  （指摘なしなら空）\n')

print('--- D) 発売日が過去（発売済みなのに発売前表示）---')
for e in NEW:
    for t in e.get('tickets', []):
        sd = t.get('startDate')
        if sd and datetime.date.fromisoformat(sd) < TODAY:
            print(f'  ⚠️ id={e["id"]} {e.get("name")} startDate={sd} | {t.get("type")}'); n += 1
print('  （指摘なしなら空）\n')

print(f'=== 再チェック指摘 {n} 件 ===')
