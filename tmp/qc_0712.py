# -*- coding: utf-8 -*-
"""7/12 新着100件(id2400-2499)の機械QC。検出のみ（--fixで半角化適用）。"""
import re, json, sys, unicodedata, datetime
sys.stdout.reconfigure(encoding='utf-8')
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
E = json.loads(m.group(2))
NEW = [e for e in E if 2400 <= e['id'] <= 2499]
TODAY = datetime.date.today().isoformat()


def half(s):
    # 全角英数字→半角。（）／〜「」『』・ は保護（NFKCだと()/~になり誤変換するので個別変換）。
    out = []
    for ch in s or '':
        o = ord(ch)
        if 0xFF10 <= o <= 0xFF19 or 0xFF21 <= o <= 0xFF3A or 0xFF41 <= o <= 0xFF5A:
            out.append(chr(o - 0xFEE0))
        elif ch == '　':
            out.append(' ')
        else:
            out.append(ch)
    return ''.join(out)


issues = {'fullwidth': [], 'emptyparen': [], 'daterev': [], 'dupcd': [], 'dupname': [], 'r9': []}
seen_cd, seen_nm = {}, {}
for e in NEW:
    i = e['id']
    for fld in ('artist', 'name', 'venue', 'dateLabel'):
        v = e.get(fld, '')
        if v != half(v):
            issues['fullwidth'].append((i, fld, v, half(v)))
    # 空カッコ会場
    if re.search(r'[（(]\s*[）)]', e.get('venue', '') + e.get('name', '') + e.get('artist', '')):
        issues['emptyparen'].append((i, e.get('venue', ''), e.get('artist', '')))
    # 日付逆転（tickets: startDate>date）
    for t in e.get('tickets', []):
        sd, d = t.get('startDate'), t.get('date')
        if sd and d and sd > d:
            issues['daterev'].append((i, t.get('type', ''), sd, d))
    # eventCd重複
    for u in [(e.get('links') or {}).get('pia', '')] + [t.get('url', '') for t in e.get('tickets', [])]:
        mm = re.search(r'event(?:Bundle)?Cd=(\w+)', u or '')
        if mm:
            cd = mm.group(1)
            if cd in seen_cd and seen_cd[cd] != i:
                issues['dupcd'].append((i, seen_cd[cd], cd))
            seen_cd.setdefault(cd, i)
    # 名前正規化重複
    nm = re.sub(r'[\s　・／/（）()]', '', unicodedata.normalize('NFKC', e.get('artist', ''))).lower()
    if nm and nm in seen_nm and seen_nm[nm] != i:
        issues['dupname'].append((i, seen_nm[nm], e.get('artist', '')))
    seen_nm.setdefault(nm, i)
    # R9年(2027公演)
    if (e.get('date', '') >= '2027-01-01') and 'R9' not in e.get('dateLabel', '') and 'R1' not in e.get('dateLabel', ''):
        issues['r9'].append((i, e.get('date', ''), e.get('dateLabel', '')))

if '--fix' in sys.argv:
    changed = 0
    for e in NEW:
        for fld in ('artist', 'name', 'venue', 'dateLabel'):
            if fld in e and e[fld] != half(e[fld]):
                e[fld] = half(e[fld]); changed += 1
    bak = f'index.html.bak_{datetime.date.today():%m%d}_qc'
    open(bak, 'w', encoding='utf-8').write(h)
    new_arr = json.dumps(E, ensure_ascii=False, indent=2)
    open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
    print(f'半角化 {changed}フィールド適用 (backup {bak})')
    sys.exit(0)

for k, v in issues.items():
    print(f'\n【{k}】{len(v)}件')
    for row in v[:20]:
        print('  ', row)
