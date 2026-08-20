# -*- coding: utf-8 -*-
"""新着プール(genre:new)の表記QC＝全角ラテン/数字の残り・角括弧ラベル・カウントダウン分布"""
import sys, io, re, json, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TODAY = datetime.date.today()
src = open('index.html', encoding='utf-8').read()
m = re.search(r'const EVENTS = (\[.*?\n\s*\]);', src, re.S)
events = json.loads(m.group(1))
new = [e for e in events if e.get('genre') == 'new']
print(f'新着プール {len(new)}件  (id {min(e["id"] for e in new)}-{max(e["id"] for e in new)})')

# 全角ラテン大文字/小文字/数字（（）／〜～ は保護対象なので対象外）
FW = re.compile(r'[Ａ-Ｚａ-ｚ０-９．－]')
print('\n=== 全角ラテン/数字が残っている箇所 ===')
hit = 0
for e in new:
    fields = [('artist', e.get('artist')), ('name', e.get('name')),
              ('venue', e.get('venue')), ('dateLabel', e.get('dateLabel'))]
    for i, t in enumerate(e.get('tickets') or []):
        fields.append((f'tickets[{i}].type', t.get('type')))
    for k, v in fields:
        if v and FW.search(v):
            print(f'  id{e["id"]} {k}: {v}')
            hit += 1
print(f'  → {hit}件' if hit else '  なし')

print('\n=== 名前に角括弧［…］が残っているもの ===')
br = [e for e in new if '［' in (e.get('name') or '') or '［' in (e.get('artist') or '')]
for e in br:
    print(f'  id{e["id"]} {e.get("name")}')
print(f'  → {len(br)}件' if br else '  なし')

print('\n=== カウントダウン分布（最も早い枠の発売/締切まで） ===')
buckets = {'発売まで4日以上': [], '発売まで2〜3日': [], '明日発売': [], '本日発売': [], '販売中': []}
for e in new:
    tks = e.get('tickets') or []
    if not tks:
        continue
    sds = [t.get('startDate') for t in tks if t.get('startDate')]
    if sds:
        sd = min(datetime.date.fromisoformat(s) for s in sds)
        d = (sd - TODAY).days
        if d >= 4:
            buckets['発売まで4日以上'].append(e['id'])
        elif d >= 2:
            buckets['発売まで2〜3日'].append(e['id'])
        elif d == 1:
            buckets['明日発売'].append(e['id'])
        elif d == 0:
            buckets['本日発売'].append(e['id'])
        else:
            buckets['販売中'].append(e['id'])
    else:
        buckets['販売中'].append(e['id'])
for k, v in buckets.items():
    print(f'  {k}: {len(v)}件')

print('\n=== 締切が公演日より後(cap逆転)・締切が過去の枠 ===')
bad = 0
for e in new:
    ed = e.get('date')
    for i, t in enumerate(e.get('tickets') or []):
        td = t.get('date')
        if not td:
            continue
        if ed and td > ed:
            print(f'  id{e["id"]} cap逆転 締切{td} > 公演{ed} | {t.get("type")}')
            bad += 1
        if datetime.date.fromisoformat(td) < TODAY:
            print(f'  id{e["id"]} 締切が過去 {td} | {t.get("type")}')
            bad += 1
print(f'  → {bad}件' if bad else '  なし')

print('\n=== _genre 下書きが空のもの（振り分け時に見る） ===')
empty = [e for e in new if not e.get('_genre')]
for e in empty:
    print(f'  id{e["id"]} {e.get("name")}  _srcgenre={e.get("_srcgenre")}')
print(f'  → {len(empty)}件' if empty else '  なし')
