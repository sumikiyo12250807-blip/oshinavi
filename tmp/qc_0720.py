# -*- coding: utf-8 -*-
"""新着(genre:"new")の2周目総点検。過去に事故った型を機械で洗う。

見る型（全部 実際にやらかした事故が元）:
  1. 空カッコ会場「全国ツアー（）」          2026-07-15,16,19
  2. 全角ローマ字/数字の混入                  feedback_newpool_fullwidth_halfwidth
  3. dateLabel に会場名が無い                 2026-07-19 キノコホテル
  4. 県名の二重表示                            2026-07-19 アインシュタイン
  5. 公演名が券種名のまま（「〜チケット（…入場分）」）
  6. 2027年公演の R9年表記漏れ                feedback_r9_year_notation
  7. prefecture が「全国」に化けている        2026-07-15 会場名の他県名を拾うバグ
  8. バッジの県名 と prefecture の不一致
  9. verified が true でない（新着タブから消える）
 10. tickets が空 / 公演日カッコ欠け
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
from check_expired import extract_events_array

PREFS = ['北海道', '青森', '岩手', '宮城', '秋田', '山形', '福島', '茨城', '栃木', '群馬', '埼玉',
         '千葉', '東京', '神奈川', '新潟', '富山', '石川', '福井', '山梨', '長野', '岐阜', '静岡',
         '愛知', '三重', '滋賀', '京都', '大阪', '兵庫', '奈良', '和歌山', '鳥取', '島根', '岡山',
         '広島', '山口', '徳島', '香川', '愛媛', '高知', '福岡', '佐賀', '長崎', '熊本', '大分',
         '宮崎', '鹿児島', '沖縄']

FW = re.compile(r'[Ａ-Ｚａ-ｚ０-９]')

events = [e for e in extract_events_array('index.html') if e.get('genre') == 'new']
print(f'新着 {len(events)}件を点検\n')

issues = []


def flag(e, kind, detail):
    issues.append((e['id'], kind, detail))


for e in events:
    eid, name = e['id'], e.get('name') or ''
    venue = e.get('venue') or ''
    pref = e.get('prefecture') or ''
    tickets = e.get('tickets') or []

    # 1. 空カッコ会場
    if re.search(r'（\s*）|\(\s*\)', venue) or not venue.strip():
        flag(e, '空カッコ会場', repr(venue))

    # 2. 全角英数
    for field in ('name', 'artist', 'venue', 'dateLabel'):
        v = e.get(field) or ''
        if FW.search(v):
            flag(e, '全角英数', f'{field}={v!r}')
    for t in tickets:
        if FW.search(t.get('type') or ''):
            flag(e, '全角英数(枠)', t.get('type'))

    # 3. dateLabel に会場名が無い
    dl = e.get('dateLabel') or ''
    if not dl:
        flag(e, 'dateLabel無し', '')
    elif venue and venue.split('（')[0][:6] not in dl:
        flag(e, 'dateLabelに会場名なし', f'venue={venue} / dateLabel={dl}')

    # 4. 県名の二重表示（バッジ内に同じ県名が2回）
    for t in tickets:
        tp = t.get('type') or ''
        for p in PREFS:
            if tp.count(p) > 1:
                flag(e, '県名二重', tp)
                break

    # 5. 公演名が券種名のまま
    if re.search(r'(チケット|パス|入場|券)\s*（[^）]*入場分）', name) or re.search(r'(ゴールド|ライト|プレミアム|VIP)チケット', name):
        flag(e, '公演名が券種名っぽい', name)

    # 6. 2027公演のR9表記
    if (e.get('date') or '').startswith('2027'):
        if not any('R9' in (t.get('type') or '') for t in tickets):
            flag(e, 'R9年表記漏れ', f'date={e.get("date")} / ' + ' | '.join(t.get('type', '') for t in tickets))

    # 7. prefecture が全国
    if pref == '全国' and venue and '全国ツアー' not in venue and 'ほか' not in venue:
        flag(e, 'prefecture全国だが単一会場', f'venue={venue}')

    # 8. バッジの県名 と prefecture の不一致
    if pref and pref != '全国':
        for t in tickets:
            m = re.search(r'（([^）]+?)\s+\d', t.get('type') or '')
            if m:
                badge_prefs = [p for p in PREFS if p in m.group(1)]
                if badge_prefs and pref not in badge_prefs:
                    flag(e, '県名不一致', f'entry={pref} / badge={m.group(1)}')

    # 9. verified
    if e.get('verified') is not True:
        flag(e, 'verified不正', repr(e.get('verified')))

    # 10. 枠なし / 公演日カッコ欠け
    if not tickets:
        flag(e, '枠ゼロ', '')
    for t in tickets:
        if not re.search(r'（[^）]*\d{1,2}/\d{1,2}[^）]*公演）', t.get('type') or ''):
            flag(e, '公演日カッコ欠け', t.get('type'))

if issues:
    print(f'🚨 要確認 {len(issues)}件\n')
    for eid, kind, detail in issues:
        print(f'  id={eid} [{kind}] {detail}')
else:
    print('✅ 機械QC 指摘ゼロ')

if '--quiet' in sys.argv:
    sys.exit(0)

print('\n--- 全件一覧（目視用）---')
for e in events:
    print(f'id={e["id"]} [{e.get("_genre")}] {e.get("name")}')
    print(f'   {e.get("prefecture")} / {e.get("venue")} / {e.get("date")}')
    for t in e.get('tickets', []):
        print(f'     ・{t.get("type")}')
