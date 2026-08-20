# -*- coding: utf-8 -*-
"""新着48件の独立監査（reconcileが見ていない所を狙う）。ネットワーク不要の構造チェック。

reconcile_pia が保証するのは「締切/発売/県/公演日/千秋楽がぴあと一致」だけ。しかも
未照合skipが17枠ある。ここでは**表記と自己矛盾**を潰す:
 ①全角ラテン/数字の残存（レビューが苦行になる＝[[feedback_newpool_fullwidth_halfwidth]]）
 ②kenshu化け（「（数字」「／残存」「【〔［の閉じ忘れ」＝[[reference_pia_tickets_tool]]）
 ③空カッコ会場・県名欠落
 ④締切>公演日のcap逆転（[[feedback_sale_end_cap_show_date]]）
 ⑤2027公演のR9年表記（[[feedback_r9_year_notation]]）
 ⑥発売前枠にsaleUntilSoldOut（[[feedback_saleuntilsoldout_presale]]）
 ⑦同一表示のバッジが2枚以上（席種ラベル落ち＝買える券が1枠に潰れる）
 ⑧ev.date が最終公演日より古い（まだ買えるのに画面から消える）
 ⑨verified / links / Amazonリンクの全角クエリ
 ⑩バッジの公演日が完全M/D形か（[[feedback_badge_date_full_form]]）
"""
import json
import re
import unicodedata
from collections import Counter

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
news = sorted([e for e in EVENTS if e.get('genre') == 'new'], key=lambda x: x['id'])

FW = re.compile(r'[Ａ-Ｚａ-ｚ０-９]')          # 全角ラテン/数字
PREF_RE = re.compile(
    r'北海道|青森|岩手|宮城|秋田|山形|福島|茨城|栃木|群馬|埼玉|千葉|東京|神奈川|新潟|富山|石川|福井|'
    r'山梨|長野|岐阜|静岡|愛知|三重|滋賀|京都|大阪|兵庫|奈良|和歌山|鳥取|島根|岡山|広島|山口|徳島|'
    r'香川|愛媛|高知|福岡|佐賀|長崎|熊本|大分|宮崎|鹿児島|沖縄|全国')

issues = []


def add(e, code, msg):
    issues.append((code, e['id'], (e.get('artist') or '')[:38], msg))


def badge_body(t):
    """締切/発売のサフィックスを落としたバッジ本体。"""
    return re.sub(r'(〜|～).*$', '', re.sub(r'\d{1,2}/\d{1,2}\s*\d{1,2}:\d{2}発売.*$', '', t or '')).strip()


for e in news:
    txts = {'artist': e.get('artist'), 'name': e.get('name'),
            'venue': e.get('venue'), 'dateLabel': e.get('dateLabel')}
    for k, v in txts.items():
        if v and FW.search(v):
            add(e, 'FW', f'{k} に全角ラテン/数字: {FW.findall(v)[:6]} | {v[:60]}')
    # 空カッコ会場
    if e.get('venue') and re.search(r'（\s*）|\(\s*\)|／／|（／', e['venue']):
        add(e, 'VENUE', f'会場に空カッコ/空要素: {e["venue"][:70]}')
    if not (e.get('venue') or '').strip():
        add(e, 'VENUE', '会場が空')
    if not (e.get('prefecture') or '').strip():
        add(e, 'PREF', 'prefecture が空')
    if not e.get('verified'):
        add(e, 'VERIFIED', 'verified が立っていない')
    az = (e.get('links') or {}).get('amazon') or ''
    if az and FW.search(az):
        add(e, 'AMZ', f'Amazonリンクのクエリが全角: {az[:90]}')

    ev_date = e.get('date') or ''
    seen_badges = Counter()
    for t in e.get('tickets') or []:
        ty = t.get('type') or ''
        if FW.search(ty):
            add(e, 'FW', f'ticket.type に全角: {FW.findall(ty)[:6]} | {ty[:60]}')
        # kenshu化け
        if '／' in ty:
            add(e, 'BREAK', f'type に全角／が残存: {ty[:60]}')
        if re.search(r'（\d', ty) and not re.search(r'（\d{1,2}/\d{1,2}', ty):
            add(e, 'BREAK', f'「（数字」化けの疑い: {ty[:60]}')
        for op, cl in (('【', '】'), ('〔', '〕'), ('［', '］'), ('（', '）')):
            if ty.count(op) != ty.count(cl):
                add(e, 'BREAK', f'{op}{cl} の対応が壊れている: {ty[:60]}')
        # 公演日の完全M/D形＋（…公演…）
        mb = re.search(r'（([^（）]*?公演[^（）]*?)）', ty)
        if not mb:
            add(e, 'BADGE', f'（…公演…）が無い: {ty[:60]}')
        else:
            inner = mb.group(1)
            if not re.search(r'\d{1,2}/\d{1,2}', inner):
                add(e, 'BADGE', f'カッコ内に M/D が無い: {ty[:60]}')
            if re.search(r'/\d{1,2}[・〜～]\d{1,2}(?![\d/])', inner):
                add(e, 'BADGE', f'略記(月が無い)が残っている: {ty[:60]}')
            if not PREF_RE.search(inner):
                add(e, 'PREF', f'バッジに県名が無い: {ty[:60]}')
        # cap逆転（締切 > 最終公演日）
        if t.get('date') and ev_date and t['date'] > ev_date and not t.get('saleUntilSoldOut'):
            add(e, 'CAP', f'締切 {t["date"]} > 千秋楽 {ev_date}: {ty[:50]}')
        # 発売前に saleUntilSoldOut
        if t.get('saleUntilSoldOut') and t.get('startDate') and t['startDate'] > '2026-07-30':
            add(e, 'SOLD', f'発売前枠に saleUntilSoldOut: {ty[:50]}')
        # 単日形（隠れ枠）
        if t.get('startDate') and t['startDate'] == t.get('date') and not t.get('saleUntilSoldOut'):
            add(e, 'HIDDEN', f'発売日==締切日の単日形: {ty[:50]}')
        # R9年（2027公演/2027締切）
        if (t.get('date') or '').startswith('2027') and 'R9' not in ty:
            add(e, 'R9', f'2027締切なのにR9年表記が無い: {ty[:60]} [date={t["date"]}]')
        seen_badges[ty] += 1
    for ty, c in seen_badges.items():
        if c > 1:
            add(e, 'DUPBADGE', f'同一バッジが{c}枚（席種ラベル落ちの疑い）: {ty[:60]}')
    # ev.date が最終公演日より古くないか（バッジ内の最大M/Dと比較・年は跨ぎを考慮しない粗チェック）
    mds = []
    for t in e.get('tickets') or []:
        mb = re.search(r'（([^（）]*?公演[^（）]*?)）', t.get('type') or '')
        if mb:
            mds += re.findall(r'(\d{1,2})/(\d{1,2})', mb.group(1))
    if mds and ev_date:
        emo, eda = int(ev_date[5:7]), int(ev_date[8:10])
        worst = max(mds, key=lambda x: (int(x[0]), int(x[1])))
        if (int(worst[0]), int(worst[1])) > (emo, eda) and not ev_date.startswith('2027'):
            add(e, 'EVDATE', f'ev.date {ev_date} よりバッジの公演日 {worst[0]}/{worst[1]} が後')

lines = [f'=== 新着 {len(news)}件の独立監査 ===', '']
cnt = Counter(c for c, *_ in issues)
if not issues:
    lines.append('指摘 0 件')
else:
    lines.append('内訳: ' + ' / '.join(f'{k}{v}' for k, v in cnt.most_common()))
    lines.append('')
    for code in [k for k, _ in cnt.most_common()]:
        lines.append(f'--- {code} ---')
        for c, i, nm, msg in issues:
            if c == code:
                lines.append(f'  id={i} {nm}')
                lines.append(f'      {msg}')
        lines.append('')
open('tmp/audit_new48_0730.txt', 'w', encoding='utf-8').write('\n'.join(lines))
print('wrote tmp/audit_new48_0730.txt  issues=%d' % len(issues))
