# -*- coding: utf-8 -*-
"""新着50件(id3622-3671)の自主チェック。index.htmlの現物だけを見る機械検査。
memory: feedback_zero_error_pipeline / feedback_harvest_dedup_check /
        feedback_newpool_fullwidth_halfwidth / feedback_r9_year_notation /
        feedback_sale_end_cap_show_date / feedback_harvest_today_sale_enddate
"""
import re, io, json, sys, datetime, unicodedata
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TODAY = datetime.date(2026, 8, 3)
h = io.open('index.html', encoding='utf-8', newline='').read()
EVENTS = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
new = [e for e in EVENTS if e.get('genre') == 'new']
old = [e for e in EVENTS if e.get('genre') != 'new']
print('新着 %d件 / 既存 %d件' % (len(new), len(old)))

def d(s):
    try:
        return datetime.date(*[int(x) for x in s.split('-')])
    except Exception:
        return None

def cds(e):
    out = set()
    for u in [(e.get('links') or {}).get('pia')] + [t.get('url') for t in e.get('tickets') or []]:
        if not u:
            continue
        for m in re.finditer(r'event(?:Bundle)?Cd=([A-Za-z0-9]+)', u):
            out.add(m.group(1))
    return out

def nfkc(s):
    return unicodedata.normalize('NFKC', s or '').replace(' ', '').lower()

ng = []
def add(cat, e, msg):
    ng.append((cat, e['id'], e.get('name', '')[:30], msg))

# 1) eventCd 重複（既存⇄新着）
oldcd = {}
for e in old:
    for c in cds(e):
        oldcd.setdefault(c, []).append(e['id'])
newcd = {}
for e in new:
    for c in cds(e):
        newcd.setdefault(c, []).append(e['id'])
for e in new:
    for c in cds(e):
        if c in oldcd:
            add('重複eventCd', e, '%s ← 既存id%s' % (c, oldcd[c]))
        if len(newcd.get(c, [])) > 1:
            add('新着内eventCd重複', e, '%s ← %s' % (c, newcd[c]))

# 2) 名前(NFKC)一致
oldname = {}
for e in old:
    oldname.setdefault(nfkc(e.get('artist') or e.get('name')), []).append(e['id'])
for e in new:
    k = nfkc(e.get('artist') or e.get('name'))
    if k in oldname:
        add('同名既存あり', e, '既存id%s（別公演か要確認）' % oldname[k][:4])

# 3) 全角ラテン/数字の残り
FW = re.compile(r'[Ａ-Ｚａ-ｚ０-９]')
for e in new:
    fields = [('artist', e.get('artist')), ('name', e.get('name')),
              ('venue', e.get('venue')), ('dateLabel', e.get('dateLabel'))]
    fields += [('ticket.type', t.get('type')) for t in e.get('tickets') or []]
    for k, v in fields:
        if v and FW.search(v):
            add('全角残り', e, '%s: %s' % (k, v[:40]))

# 4) 同一バッジ文字列が2枚以上（ラベル落ち）
for e in new:
    ts = [t.get('type', '') for t in e.get('tickets') or []]
    for t in set(ts):
        if ts.count(t) > 1:
            add('同一バッジ重複', e, '%s ×%d' % (t[:40], ts.count(t)))

# 5) 日付系
for e in new:
    ev = d(e.get('date') or '')
    if not ev:
        add('公演日なし', e, str(e.get('date')))
        continue
    if ev < TODAY:
        add('公演日が過去', e, e['date'])
    if not (e.get('tickets') or []):
        add('枠ゼロ', e, '-')
    for t in e.get('tickets') or []:
        td = d(t.get('date') or '')
        sd = d(t.get('startDate') or '') if t.get('startDate') else None
        if not td:
            add('枠に日付なし', e, t.get('type', '')[:40])
            continue
        if td > ev:
            add('cap逆転(締切>公演日)', e, '%s 締切%s 公演%s' % (t.get('type', '')[:26], t['date'], e['date']))
        if td < TODAY:
            add('締切が過去', e, '%s %s' % (t.get('type', '')[:26], t['date']))
        if sd:
            if sd == td and sd <= TODAY:
                add('隠れ枠(発売日=締切で当日以前)', e, '%s %s' % (t.get('type', '')[:26], t['date']))
            if sd <= TODAY + datetime.timedelta(days=1):
                add('発売間近(実は販売中の疑い→抜き取り)', e, '%s 発売%s' % (t.get('type', '')[:26], t['startDate']))

# 6) URL品質
for e in new:
    p = (e.get('links') or {}).get('pia')
    if not p:
        add('links.pia無し', e, str(e.get('links')))
    elif 'event.do?event' not in p:
        add('個別URLでない', e, p[:70])
    for t in e.get('tickets') or []:
        u = t.get('url')
        if u and 'rlsCd=' in u:
            add('rlsCd形URL', e, u[:70])

# 7) 県
for e in new:
    if not e.get('prefecture'):
        add('県欠落', e, '-')
    elif e['prefecture'] in ('全国', '未定'):
        add('県が全国/未定', e, e['prefecture'])

# 8) verified
for e in new:
    if e.get('verified') is not True:
        add('verified欠落', e, str(e.get('verified')))

# 9) R9年表記（2027以降の公演）
for e in new:
    ev = d(e.get('date') or '')
    if ev and ev.year >= 2027:
        for t in e.get('tickets') or []:
            typ = t.get('type', '')
            head = typ.split('）')[0]
            if 'R' not in head:
                add('R9年表記なし', e, '%s（公演%s）' % (typ[:40], e['date']))

# 10) 情報
print('価格null %d/%d件' % (sum(1 for e in new if not e.get('price')), len(new)))
print('枠合計 %d' % sum(len(e.get('tickets') or []) for e in new))

print('\n=== 指摘 %d件 ===' % len(ng))
cats = {}
for c, i, n, m in ng:
    cats.setdefault(c, []).append((i, n, m))
for c in sorted(cats, key=lambda x: -len(cats[x])):
    print('\n■ %s : %d件' % (c, len(cats[c])))
    for i, n, m in cats[c]:
        print('   id%s %s | %s' % (i, n, m))
