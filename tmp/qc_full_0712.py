# -*- coding: utf-8 -*-
"""7/12 新着100件(2400-2499)の総点検。機械で拾える異常を全部出す。"""
import re, json, sys, unicodedata, collections
sys.stdout.reconfigure(encoding='utf-8')
h = open('index.html', encoding='utf-8').read()
E = json.loads(re.search(r'const EVENTS = (\[.*?\]);', h, re.S).group(1))
NEW = [e for e in E if 2400 <= e['id'] <= 2499]
OLD = [e for e in E if e['id'] < 2400]
TODAY = '2026-07-12'
out = []


def w(s): out.append(s)


def hasmojibake(s):
    # 置換文字・制御・私用領域・全角化けの典型
    return any(ord(c) in (0xFFFD,) or 0xE000 <= ord(c) <= 0xF8FF for c in (s or ''))


# 1) 文字化け・置換文字
mo = [(e['id'], f) for e in NEW for f in ('artist', 'name', 'venue', 'dateLabel')
      if hasmojibake(e.get(f, ''))]
w(f'【1 文字化け】{len(mo)}件: {mo[:10]}')

# 2) 空フィールド
empt = [(e['id'], f) for e in NEW for f in ('artist', 'venue', 'date', 'genre')
        if not e.get(f)]
w(f'【2 空フィールド】{len(empt)}件: {empt[:10]}')

# 3) 空カッコ（会場/券種）
ep = []
for e in NEW:
    if re.search(r'[（(]\s*[）)]', e.get('venue', '')):
        ep.append((e['id'], 'venue', e.get('venue')))
    for t in e.get('tickets', []):
        if re.search(r'[（(]\s*[）)]', t.get('type', '')):
            ep.append((e['id'], 'type', t.get('type')))
w(f'【3 空カッコ】{len(ep)}件')
for x in ep[:10]: w(f'    {x}')

# 4) 券種の飾り記号（●○★◎@※など strip漏れ）
deco = []
for e in NEW:
    for t in e.get('tickets', []):
        if re.search(r'[●○★☆◎@＠※]', t.get('type', '')):
            deco.append((e['id'], t.get('type')))
w(f'【4 券種飾り記号】{len(deco)}件')
for x in deco[:10]: w(f'    {x}')

# 5) 日付逆転（tickets startDate>date）＋ date<今日（過去公演）
drev = [(e['id'], t.get('type')) for e in NEW for t in e.get('tickets', [])
        if t.get('startDate') and t.get('date') and t['startDate'] > t['date']]
past = [(e['id'], e.get('date')) for e in NEW if e.get('date', '') < TODAY]
w(f'【5 日付逆転】{len(drev)}件 / 過去公演date {len(past)}件: {past[:8]}')

# 6) R9年（2027公演でバッジにR9無し）
r9 = []
for e in NEW:
    for t in e.get('tickets', []):
        # 公演日が2027なのにR9表記が無いバッジ
        typ = t.get('type', '')
        if t.get('date', '') >= '2027-01-01' and 'R9' not in typ and 'R10' not in typ and '2027' not in typ:
            r9.append((e['id'], typ))
w(f'【6 R9年表記漏れ疑い】{len(r9)}件')
for x in r9[:10]: w(f'    {x}')

# 7) 新着 vs 既存の重複（eventCd / 正規化名）
old_cd = set()
for e in OLD:
    for u in [(e.get('links') or {}).get('pia', '')] + [t.get('url', '') for t in e.get('tickets', [])]:
        m = re.search(r'event(?:Bundle)?Cd=(\w+)', u or '')
        if m: old_cd.add(m.group(1))


def nm(s):
    return re.sub(r'[\s　・／/（）()【】「」『』’\'"!！\-—]', '', unicodedata.normalize('NFKC', s or '')).lower()
old_nm = {nm(e.get('artist', '')): e['id'] for e in OLD}
dupcd, dupnm = [], []
for e in NEW:
    for u in [(e.get('links') or {}).get('pia', '')] + [t.get('url', '') for t in e.get('tickets', [])]:
        m = re.search(r'event(?:Bundle)?Cd=(\w+)', u or '')
        if m and m.group(1) in old_cd:
            dupcd.append((e['id'], m.group(1)))
    k = nm(e.get('artist', ''))
    if k and k in old_nm:
        dupnm.append((e['id'], old_nm[k], e.get('artist', '')[:30]))
w(f'【7 既存重複 eventCd】{len(dupcd)}件: {dupcd[:10]}')
w(f'【7 既存重複 正規化名】{len(dupnm)}件')
for x in dupnm[:12]: w(f'    new{x[0]} == old{x[1]} : {x[2]}')

# 8) verified / links.pia の有無
noveri = [e['id'] for e in NEW if not e.get('verified')]
nopia = [e['id'] for e in NEW if 'pia' not in ((e.get('links') or {}).get('pia', '') or '')]
w(f'【8 verified無】{len(noveri)}件: {noveri[:10]} / links.pia無 {len(nopia)}件: {nopia[:10]}')

# 9) ジャンル下書き _genre と _piaSub の整合（_piaSub空/その他＝要人手）
need = []
for e in NEW:
    ps = e.get('_piaSub', '')
    if (not ps) or ('その他' in ps):
        need.append((e['id'], repr(ps), e.get('_genre'), (e.get('artist') or '')[:24]))
w(f'【9 _piaSub空/その他＝ジャンル要確認】{len(need)}件')
for x in need[:20]: w(f'    {x}')

# 10) 価格が入っている新着（原則2サイト一致のみ・要確認）
pr = [(e['id'], e.get('price')) for e in NEW if e.get('price')]
w(f'【10 価格入り】{len(pr)}件: {pr[:10]}')

open('tmp/qc_full_0712.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(out))
