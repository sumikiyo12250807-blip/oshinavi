# -*- coding: utf-8 -*-
"""新着バッチ(id4226-4275)の人手レビュー代替チェック。
機械ゲート(reconcile/check_badges)が見ない観点だけを見る:
 A. 2027公演のR9年表記（feedback_r9_year_notation）
 B. 販売終了日 > 公演日 の cap逆転（feedback_sale_end_cap_show_date）
 C. 抽選結果発表を受付枠にしていないか（feedback_capture_all_deadlines_on_add）
 D. venue/price/links の欠け（feedback_require_specific_url / feedback_link_quality）
 E. 会場名に他県名が入る罠・prefecture=全国なのに単一会場（reference_pia_tickets_tool）
 F. 締切/発売が近すぎる子（feedback_harvest_source_order_and_far_deadline）
"""
import re, json, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

TODAY = datetime.date.today()
h = open('index.html', encoding='utf-8', newline='').read()
EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
new = [e for e in EV if 4226 <= e.get('id', 0) <= 4275]
d = lambda s: datetime.date.fromisoformat(s) if s else None


def out(tag, rows):
    print('\n【%s】%d件' % (tag, len(rows)))
    for r in rows:
        print('   ', r)


# A. 2027以降の公演にR9年が入っているか
a = []
for e in new:
    if (e.get('date') or '') >= '2027-01-01':
        for t in e.get('tickets') or []:
            ty = t.get('type') or ''
            if '公演' in ty and 'R9年' not in ty and 'R10年' not in ty:
                a.append((e['id'], e.get('date'), ty))
out('A. 2027公演のR9年表記もれ', a)

# B. cap逆転（販売終了日が公演日より後）
b = []
for e in new:
    ed = d(e.get('date'))
    for t in e.get('tickets') or []:
        td = d(t.get('date'))
        if ed and td and td > ed and not t.get('saleUntilSoldOut'):
            b.append((e['id'], (e.get('name') or '')[:26], '公演%s < 締切%s' % (ed, td), t.get('type')))
out('B. 販売終了日>公演日 の逆転', b)

# C. 抽選結果発表・結果発表待ちが枠に混ざっていないか
c = [(e['id'], (e.get('name') or '')[:26], t.get('type'))
     for e in new for t in (e.get('tickets') or [])
     if re.search(r'結果発表|当選発表|抽選結果', t.get('type') or '')]
out('C. 抽選結果発表が枠に混入', c)

# D. 欠け
dd = []
for e in new:
    if not (e.get('venue') or '').strip():
        dd.append((e['id'], 'venue空'))
    if not ((e.get('links') or {}).get('pia')):
        dd.append((e['id'], 'pia link無し'))
    if not (e.get('dateLabel') or '').strip():
        dd.append((e['id'], 'dateLabel空'))
out('D. venue/link/dateLabel の欠け', dd)

# E. prefecture=全国 なのに会場が1つ（＝県が取れていない疑い）
ee = [(e['id'], (e.get('name') or '')[:30], e.get('venue'))
      for e in new
      if e.get('prefecture') == '全国' and '／' not in (e.get('venue') or '')
      and 'ツアー' not in (e.get('venue') or '')]
out('E. 全国表記だが単一会場（県が取れてない疑い）', ee)

# F. 発売/締切が3日以内の子（遠い順に取る方針からの外れ）
f = []
for e in new:
    for t in e.get('tickets') or []:
        key = t.get('startDate') or t.get('date')
        if key and (d(key) - TODAY).days <= 3:
            f.append((e['id'], (e.get('name') or '')[:26], t.get('type')))
out('F. 発売/締切まで3日以内', f)

# 参考: 公演日が最も遠い/近い
ds = sorted((e.get('date'), e['id'], (e.get('name') or '')[:30]) for e in new)
print('\n公演日レンジ:', ds[0][0], '〜', ds[-1][0])
print('2027年以降の公演:', [(x[1], x[0]) for x in ds if x[0] >= '2027-01-01'])
