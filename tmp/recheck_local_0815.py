# -*- coding: utf-8 -*-
"""新着プール(id4276-4325)を「登録データだけ」で点検する（実ページ照合の前段）。
reconcile_pia とは別の観点で、表示に出る嘘・欠けを洗う。
 A cap逆転     : ticket.date が公演日より後（feedback_sale_end_cap_show_date）
 B 過去日      : ticket.date が今日より前 / ev.date が今日より前
 C 千秋楽ズレ  : ev.date がバッジの最終公演日と食い違う
 D 県欠落      : prefecture 空 or バッジに県が無い
 E 近すぎ締切  : 買える枠の最も遅い締切が今日/明日で終わる（載せる価値が薄い）
 F バッジ形式  : （…公演…）が無い / M/D が無い / 略記の残り
 G 売切混入    : soldout / saleEnded が付いた枠
 H URL欠落    : links.pia も ticket.url も無い
"""
import re, json, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today()
TS = TODAY.isoformat()

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
E = json.loads(m.group(2))
NEW = [e for e in E if e.get('genre') == 'new']

PREFS = ('北海道|青森|岩手|宮城|秋田|山形|福島|茨城|栃木|群馬|埼玉|千葉|東京|神奈川|新潟|富山|石川|福井|'
         '山梨|長野|岐阜|静岡|愛知|三重|滋賀|京都|大阪|兵庫|奈良|和歌山|鳥取|島根|岡山|広島|山口|徳島|'
         '香川|愛媛|高知|福岡|佐賀|長崎|熊本|大分|宮崎|鹿児島|沖縄|全国')
PREF_RE = re.compile(PREFS)
MD = re.compile(r'(\d{1,2})/(\d{1,2})')
PAREN = re.compile(r'（[^（）]*?公演[^（）]*?）')
ABBR = re.compile(r'\d{1,2}/\d{1,2}[・〜]\d{1,2}(?![\d/])')

issues = []


def show_dates(ty):
    """バッジの（… M/D公演）から公演日(月,日)を全部拾う。"""
    out = []
    for p in PAREN.findall(ty or ''):
        for mm, dd in MD.findall(p):
            out.append((int(mm), int(dd)))
    return out


def to_date(md, base_year):
    mm, dd = md
    y = base_year
    try:
        return datetime.date(y, mm, dd)
    except ValueError:
        return None


for e in NEW:
    eid, nm = e['id'], e['name']
    evd = e.get('date') or ''
    tks = e.get('tickets') or []
    if not tks:
        issues.append(('H', eid, nm, '枠が0件'))
    if not (e.get('links') or {}).get('pia'):
        if not any(t.get('url') for t in tks):
            issues.append(('H', eid, nm, 'ぴあURLも枠URLも無い'))
    if not e.get('prefecture'):
        issues.append(('D', eid, nm, 'prefecture が空'))
    if evd and evd < TS:
        issues.append(('B', eid, nm, 'ev.date=%s が過去' % evd))

    ev_year = int(evd[:4]) if evd[:4].isdigit() else TODAY.year
    last_show = None
    latest_close = None
    for t in tks:
        ty = t.get('type') or ''
        td = t.get('date') or ''
        if t.get('soldout') or t.get('saleEnded'):
            issues.append(('G', eid, nm, '売切/販売終了の枠が混入: %s' % ty[:40]))
        if td and td < TS:
            issues.append(('B', eid, nm, '枠の締切が過去 %s | %s' % (td, ty[:40])))
        # バッジ形式
        if not PAREN.search(ty):
            issues.append(('F', eid, nm, '（…公演…）が無い: %s' % ty[:40]))
        elif not show_dates(ty):
            issues.append(('F', eid, nm, 'カッコ内にM/Dが無い: %s' % ty[:40]))
        if ABBR.search(ty):
            issues.append(('F', eid, nm, '略記が残っている: %s' % ty[:40]))
        if not PREF_RE.search(ty):
            issues.append(('D', eid, nm, 'バッジに県が無い: %s' % ty[:40]))
        # cap逆転
        for md in show_dates(ty):
            d = to_date(md, ev_year)
            if d and td and td > d.isoformat():
                # 年またぎ（12月公演で1月締切など）は誤検出しやすいので月差で緩める
                if not (md[0] <= 3 and int(td[5:7]) >= 10):
                    issues.append(('A', eid, nm, '締切%s > 公演%d/%d | %s' % (td, md[0], md[1], ty[:34])))
            if d and (last_show is None or d > last_show):
                last_show = d
        if td and (latest_close is None or td > latest_close):
            latest_close = td
    # 千秋楽ズレ
    if last_show and evd and last_show.isoformat() != evd:
        issues.append(('C', eid, nm, 'ev.date=%s だがバッジ最終公演=%s' % (evd, last_show)))
    # 近すぎ締切
    if latest_close and latest_close <= (TODAY + datetime.timedelta(days=1)).isoformat():
        has_start = any((t.get('startDate') or '') >= TS for t in tks)
        if not has_start:
            issues.append(('E', eid, nm, '買える枠の最終締切が %s（明日までに終わる）' % latest_close))

order = {}
for k, eid, nm, msg in issues:
    order.setdefault(k, []).append((eid, nm, msg))

print('新着 %d件を点検 / 指摘 %d件' % (len(NEW), len(issues)))
for k in sorted(order):
    print('\n=== [%s] %d件 ===' % (k, len(order[k])))
    for eid, nm, msg in order[k]:
        print('  id%-5d %-30s %s' % (eid, nm[:30], msg))
