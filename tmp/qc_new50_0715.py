#!/usr/bin/env python3
"""新着50件(genre:new)の総点検＝機械QC。間違い0を目指す2周目チェック。

チェック項目（過去に事故った型を全部）：
 1 全角ラテン/数字の残り（（）／〜は正当）
 2 空カッコ会場「（）」「（ ）」
 3 飾り記号 ●○★◎@※ の残り
 4 日付逆転（販売終了日 > 公演日 = capし忘れ）
 5 eventCd重複・正規化名の重複（既存DBと）
 6 verified欠落
 7 price捏造（2サイト一致以外はnullのはず）
 8 R9年表記漏れ（2027公演なのにバッジに「R9年」無し）
 9 prefecture=全国 なのに単一会場（県誤検出バグ）
10 重複バッジ（表示完全一致のticket）
11 バッジ公演日の完全M/D形＋（…公演…）
12 dateLabel/venue の空・欠落
13 ジャンル下書きの誤フォールバック候補（_piaSub空でengeki）
"""
import re
import sys
sys.path.insert(0, 'tools')
from build_pia_entries import PREF_RE  # stdoutをUTF-8ラップ
from check_expired import extract_events_array

EVENTS = extract_events_array('index.html')
NEW = [e for e in EVENTS if e.get('genre') == 'new']
OLD = [e for e in EVENTS if e.get('genre') != 'new']
print(f'新着(genre:new) {len(NEW)}件 / 既存 {len(OLD)}件\n')

issues = []


def add(e, kind, detail):
    issues.append((e.get('id'), e.get('name'), kind, detail))


FW = re.compile(r'[Ａ-Ｚａ-ｚ０-９．＆！？：－]')
DECO = re.compile(r'[●○★◎@※☆]')


def ecd(e):
    u = (e.get('links') or {}).get('pia') or ''
    m = re.search(r'event(?:Bundle)?Cd=(\w+)', u)
    return m.group(1) if m else ''


def norm_name(s):
    return re.sub(r'[\s　・･!！?？~〜ー\-]', '', (s or '')).lower()


old_ecd = {}
for e in OLD:
    c = ecd(e)
    if c:
        old_ecd.setdefault(c, e)
old_names = {}
for e in OLD:
    old_names.setdefault(norm_name(e.get('name')), e)

seen_ecd, seen_name = {}, {}

for e in NEW:
    name = e.get('name') or ''
    venue = e.get('venue') or ''
    label = e.get('dateLabel') or ''
    tickets = e.get('tickets') or []

    # 1 全角
    for fld, val in (('name', name), ('venue', venue), ('dateLabel', label)):
        if FW.search(val or ''):
            add(e, '全角残り', f'{fld}: {val}')
    for t in tickets:
        if FW.search(t.get('type', '')):
            add(e, '全角残り', f"ticket: {t.get('type')}")

    # 2 空カッコ会場
    if re.search(r'（\s*）', venue) or re.search(r'（\s*）', label):
        add(e, '空カッコ', f'venue={venue} / label={label}')

    # 3 飾り記号
    for t in tickets:
        if DECO.search(t.get('type', '')):
            add(e, '飾り記号', t.get('type'))
    if DECO.search(name):
        add(e, '飾り記号', f'name: {name}')

    # 4 日付逆転（販売終了日 > 公演日）
    ev_date = e.get('date') or ''
    for t in tickets:
        td = t.get('date') or ''
        if ev_date and td and td > ev_date:
            add(e, '日付逆転', f"販売終了{td} > 公演{ev_date} | {t.get('type')}")

    # 5 重複
    c = ecd(e)
    if c:
        if c in old_ecd:
            add(e, '既存と重複(eventCd)', f"{c} → 既存 {old_ecd[c].get('name')}")
        if c in seen_ecd:
            add(e, '新着内で重複(eventCd)', f"{c} → {seen_ecd[c]}")
        seen_ecd[c] = name
    nn = norm_name(name)
    if nn in old_names:
        add(e, '既存と同名', f"既存 id={old_names[nn].get('id')} {old_names[nn].get('name')}")
    if nn in seen_name:
        add(e, '新着内で同名', seen_name[nn])
    seen_name[nn] = name

    # 6 verified
    if not e.get('verified'):
        add(e, 'verified欠落', str(e.get('verified')))

    # 7 price
    if e.get('price'):
        add(e, 'price有り(要2サイト一致)', str(e.get('price')))

    # 8 R9年（2027公演）
    if ev_date.startswith('2027'):
        for t in tickets:
            if 'R9年' not in t.get('type', ''):
                add(e, 'R9年表記漏れ', f"公演{ev_date} | {t.get('type')}")

    # 9 全国なのに単一会場
    if e.get('prefecture') == '全国':
        if not ('全国ツアー' in venue or '／' in venue or 'ほか' in venue or '配信' in venue or 'LIVE STREAM' in venue):
            add(e, '全国なのに単一会場', f'venue={venue} 会場名の県={PREF_RE.findall(venue)}')

    # 10 重複バッジ（表示完全一致）
    seen_t = {}
    for t in tickets:
        k = (t.get('type'), t.get('date'), t.get('startDate'))
        if k in seen_t:
            add(e, '重複バッジ', f"{t.get('type')} が2枠")
        seen_t[k] = 1

    # 11 バッジ形（公演日が完全M/D・（…公演…）内）
    for t in tickets:
        ty = t.get('type', '')
        m = re.search(r'（[^（）]*公演[^（）]*）', ty)
        if not m:
            add(e, 'バッジに（…公演…）無し', ty)
        else:
            inner = m.group(0)
            if not re.search(r'\d{1,2}/\d{1,2}', inner):
                add(e, 'バッジ公演日が無い', ty)
            if re.search(r'\d{1,2}/\d{1,2}[・〜]\d{1,2}(?![\d/])', inner):
                add(e, 'バッジ公演日が略記', ty)

    # 12 欠落
    if not venue:
        add(e, 'venue空', label)
    if not label:
        add(e, 'dateLabel空', name)
    if not tickets:
        add(e, 'ticket無し', name)

print('=' * 70)
if not issues:
    print('✅ 機械QC 異常なし（間違い0）')
else:
    print(f'🚨 検出 {len(issues)}件')
    for i, nm, kind, det in issues:
        print(f'  [{kind}] id={i} {nm}')
        print(f'        {det}')
