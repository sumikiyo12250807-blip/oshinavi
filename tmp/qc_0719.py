# -*- coding: utf-8 -*-
"""新着50件(id2865-2914)の総点検。全角/空カッコ/日付逆転/R9表記/価格/verified/類似名。"""
import re, json, sys, unicodedata
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
E = json.loads(m.group(2))
NEW = [e for e in E if 2865 <= (e.get('id') or 0) <= 2914]
print('対象', len(NEW), '件\n')

# （）／〜～ は意味のある記号として保護（memory: feedback_newpool_fullwidth_halfwidth）
PROTECT = set('（）／〜～・“”')

def fw(s):
    """保護記号以外の全角ローマ字/数字を検出"""
    if not isinstance(s, str):
        return ''
    return ''.join(c for c in s
                   if unicodedata.east_asian_width(c) == 'F' and c not in PROTECT)

issues = 0
for e in NEW:
    tag = f"id={e['id']} {e.get('name')}"
    for k in ('name', 'artist', 'venue', 'dateLabel'):
        bad = fw(e.get(k) or '')
        if bad:
            print(f'[全角] {tag} .{k} = {e.get(k)!r} → {bad}'); issues += 1
    for t in e.get('tickets', []):
        bad = fw(t.get('type') or '')
        if bad:
            print(f'[全角] {tag} ticket.type = {t.get("type")!r} → {bad}'); issues += 1
    v = e.get('venue') or ''
    if re.search(r'（\s*）|\(\s*\)', v):
        print(f'[空カッコ] {tag} venue={v!r} pref={e.get("prefecture")}'); issues += 1
    ev = e.get('date')
    for t in e.get('tickets', []):
        if t.get('date') and ev and t['date'] > ev:
            print(f'[日付逆転] {tag} ev.date={ev} < ticket.date={t["date"]} ({t.get("type")})'); issues += 1
    if ev and ev >= '2027-01-01':
        blob = (e.get('dateLabel') or '') + ''.join(t.get('type', '') for t in e.get('tickets', []))
        if 'R9' not in blob:
            print(f'[R9漏れ] {tag} ev.date={ev} dateLabel={e.get("dateLabel")!r}'); issues += 1
    if not e.get('verified'):
        print(f'[verified無] {tag}'); issues += 1
    if e.get('price'):
        print(f'[価格] {tag} price={e.get("price")!r}'); issues += 1
    if not e.get('tickets'):
        print(f'[枠ゼロ] {tag}'); issues += 1

def nm(s):
    return re.sub(r'[\s　・／/（）()【】0-9０-９]', '', (s or '')).lower()
seen = {}
for e in NEW:
    seen.setdefault(nm(e.get('name'))[:10], []).append(e)
print('\n--- 統合候補（名前が近い新着同士）---')
for k, v in seen.items():
    if len(v) > 1:
        for e in v:
            print(f"  id={e['id']} {e.get('name')}")
            print(f"      公演日={e.get('date')} 会場={e.get('venue')}")
            for t in e.get('tickets', []):
                print(f"      枠: {t.get('type')} | 販売={t.get('date')} start={t.get('startDate')}")
        print()

print(f'=== QC指摘 {issues} 件 ===')
