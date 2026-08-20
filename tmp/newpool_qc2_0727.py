# -*- coding: utf-8 -*-
"""新着プールの総点検（機械ゲートの後に回す内容チェック）
   ①全角ラテン/数字 ②角括弧の地域ラベル ③締切の逆転/期限切れ ④_genre空欄
   ⑤同一エントリ内でバッジ文言が完全重複（券種名落ちの兆候＝ドラクエで見つけた穴）
   ⑥全国ツアーなのに会場が1つしか無い/空カッコ ⑦価格・URLの欠落
"""
import sys, io, re, json, datetime, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TODAY = datetime.date.today()
src = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'const EVENTS = (\[.*?\n\s*\]);', src, re.S)
events = json.loads(m.group(1))
new = sorted([e for e in events if e.get('genre') == 'new'], key=lambda e: e['id'])
print(f'新着プール {len(new)}件 (id {new[0]["id"]}-{new[-1]["id"]})\n')

FW = re.compile(r'[Ａ-Ｚａ-ｚ０-９．－]')


def sec(t):
    print('=' * 4, t)


sec('① 全角ラテン/数字の残り')
n = 0
for e in new:
    fs = [('artist', e.get('artist')), ('name', e.get('name')),
          ('venue', e.get('venue')), ('dateLabel', e.get('dateLabel'))]
    fs += [(f'tickets[{i}]', t.get('type')) for i, t in enumerate(e.get('tickets') or [])]
    for k, v in fs:
        if v and FW.search(v):
            print(f'  id{e["id"]} {k}: {v}'); n += 1
print('  なし' if not n else f'  → {n}件')

sec('② 名前の角括弧［…］')
b = [e for e in new if '［' in (e.get('name') or '')]
for e in b:
    print(f'  id{e["id"]} {e["name"]}')
print('  なし' if not b else f'  → {len(b)}件')

sec('③ 締切の逆転・期限切れ')
n = 0
for e in new:
    for t in e.get('tickets') or []:
        d = t.get('date')
        if not d:
            print(f'  id{e["id"]} dateが無い枠: {t.get("type")}'); n += 1; continue
        if e.get('date') and d > e['date']:
            print(f'  id{e["id"]} cap逆転 締切{d}>公演{e["date"]} | {t.get("type")}'); n += 1
        if datetime.date.fromisoformat(d) < TODAY:
            print(f'  id{e["id"]} 締切が過去 {d} | {t.get("type")}'); n += 1
print('  なし' if not n else f'  → {n}件')

sec('④ _genre が空')
b = [e for e in new if not e.get('_genre')]
for e in b:
    print(f'  id{e["id"]} {e["name"][:50]} (_piaSub={e.get("_piaSub")!r})')
print('  なし' if not b else f'  → {len(b)}件')

sec('⑤ 同一エントリ内でバッジ文言が完全重複（券種名落ちの疑い）')
n = 0
for e in new:
    c = collections.Counter(t.get('type') for t in (e.get('tickets') or []))
    for typ, cnt in c.items():
        if cnt > 1:
            print(f'  id{e["id"]} 同文言×{cnt}: {typ}')
            print(f'      {e["name"][:50]}'); n += 1
print('  なし' if not n else f'  → {n}件')

sec('⑥ 会場の異常（空カッコ・全国ツアーなのに1会場）')
n = 0
for e in new:
    v = e.get('venue') or ''
    if '（）' in v or v.strip() in ('', '全国ツアー', '全国ツアー（）'):
        print(f'  id{e["id"]} venue={v!r}'); n += 1
    mm = re.match(r'全国ツアー（(.*)）$', v)
    if mm and len(mm.group(1).split('／')) < 2:
        print(f'  id{e["id"]} 全国ツアーなのに1会場: {v}'); n += 1
print('  なし' if not n else f'  → {n}件')

sec('⑦ 購入URLが無い枠')
n = 0
for e in new:
    links = e.get('links') or {}
    has_entry_url = any(links.get(k) for k in ('pia', 'rakuten', 'eplus', 'lawson'))
    if not has_entry_url:
        print(f'  id{e["id"]} エントリにも購入リンクが無い: {e["name"][:44]}'); n += 1
print('  なし' if not n else f'  → {n}件')

sec('⑧ カウントダウン分布')
buck = collections.Counter()
for e in new:
    sds = [t['startDate'] for t in (e.get('tickets') or []) if t.get('startDate')]
    if not sds:
        buck['販売中'] += 1; continue
    d = (min(datetime.date.fromisoformat(s) for s in sds) - TODAY).days
    buck['発売まで4日以上' if d >= 4 else '発売まで2〜3日' if d >= 2 else
         '明日発売' if d == 1 else '本日発売' if d == 0 else '販売中'] += 1
for k, v in buck.items():
    print(f'  {k}: {v}件')
