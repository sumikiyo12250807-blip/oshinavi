# -*- coding: utf-8 -*-
"""バッジ公演日のオレンジ強調チェッカー（投入前に必ず回す）。
memory: feedback_badge_date_full_form の機械チェックを実装。
highlightShowDate は バッジ内の \\d{1,2}/\\d{1,2}(-\\d{1,2})? を全てオレンジ強調する
（カッコ有無・全角半角・〔〕問わず。ただし直後が発売/受付/販売/締切の販売日は除外）。
→ 残る唯一のNG = 略記/半端範囲「8/8・9」「8/27〜30」(2日目に月が無く単独数字でマッチしない)。
使い方: python tools/check_badges.py [--all]   (既定: genre=="new" のみ)
"""
import re, io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ALL = '--all' in sys.argv
src = open('index.html', encoding='utf-8').read()
m = re.search(r'=\s*(\[\s*\{.*?\}\s*\]);', src, re.S)
data = json.loads(m.group(1))

def badge(raw):
    s = re.sub(r'\s*〜\s*\d{1,2}/\d{1,2}(?:\s*\d{1,2}:\d{2})?\s*$', '', raw)
    s = re.sub(r'\s*\d{1,2}/\d{1,2}(?:\s*\d{1,2}:\d{2})?\s*(?:発売開始|発売予定|発売|販売開始|受付開始|受付)\s*$', '', s).strip() or raw
    return s

abbr_re = re.compile(r'/\d{1,2}[・〜]\d{1,2}(?![\d/])')   # 略記/半端範囲(2日目に月なし)
date_re = re.compile(r'\d{1,2}/\d{1,2}')

ng = []
for e in data:
    if not ALL and e.get('genre') != 'new':
        continue
    # verified欠落チェック（verified!==trueだと matchEvent が新着タブから除外する）
    if e.get('verified') is not True:
        ng.append((e['id'], e.get('name', '')[:24], '(エントリ全体)', 'verified:true が無い→新着タブに出ない'))
    for t in e.get('tickets', []):
        typ = t.get('type', '')
        b = badge(typ)
        reasons = []
        if abbr_re.search(b):
            reasons.append('略記/半端範囲(2日目に月なし)')
        if '公演' in b and not date_re.search(b):
            reasons.append('公演バッジなのに公演日(M/D)が無い')   # 例「各公演」→ぴあの期間日付を入れる
        # kenshuパース化けガード（2026-06-23 JUJU「一般発売（９」事故の恒久検出）。
        # 正常な type は「券種名（県 M/D公演）…」。県名(漢字)の前に全角／や数字が来たら化け。
        if '／' in typ:
            reasons.append('券種名に全角／残存(kenshuパース化け)')
        if re.search(r'[【〔［＜]', typ):
            reasons.append('券種名に角/山カッコ【〔［＜残存(kenshu化け)')
        if re.search(r'（[０-９0-9]', typ):
            reasons.append('（の直後が数字＝券種名化け疑い')
        if typ.count('（') != typ.count('）'):
            reasons.append('丸カッコ（）が不均衡＝パース化け疑い')
        if reasons:
            ng.append((e['id'], e.get('name', '')[:24], b, ' / '.join(reasons)))

scope = '全エントリ' if ALL else 'genre:new'
if not ng:
    print(f'OK: {scope} のバッジ公演日は全てオレンジ強調される形になっている（略記なし・日付欠落なし）。')
else:
    print(f'NG {len(ng)}件（{scope}）— 修正すること:')
    for i, nm, b, r in ng:
        print(f'  id={i} [{r}] {b}  / {nm}')
    sys.exit(1)
