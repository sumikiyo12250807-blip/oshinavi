# -*- coding: utf-8 -*-
"""統合＝既存エントリに「別ページの公演」の枠を足す。**枠にそのページのURLを焼き込む**。

  python tmp/merge_with_urls_0910.py            … 調べるだけ
  python tmp/merge_with_urls_0910.py --apply

🚨2026-09-10 にここで失敗した＝`refresh_deadlines` にそのまま流したら、
   足した枠が **url を持たないまま** 入り、押すと既存の links.pia（別会場）へ飛ぶ状態になった。
   単独URLのビルドは「links.pia があるから」と ticket.url を付けないので、
   **別エントリへ移す時は移す側でURLを焼き込まないといけない**
   （[[feedback_tour_per_ticket_url]]「エントリを畳む前にurl空の枠へカードリンクを焼き込む」）。

やること:
 ・足す枠には**そのページのURL**を必ず入れる
 ・既存の url 空の枠には**既存の links.pia** を焼き込む（同じ理由で飛び先が壊れるため）
 ・骨格（券種名＋（…公演））が既存にある枠は触らない（締切の更新は refresh の担当）
 ・会場が増えるので dateLabel / venue / prefecture / date を union で作り直す
"""
import io
import json
import re
import sys

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')

APPLY = '--apply' in sys.argv
WD = '月火水木金土日'


def head(ty):
    m = re.match(r'^(.*?（[^（）]*公演）)', ty or '')
    return m.group(1) if m else (ty or '')


def jp(iso_s):
    import datetime
    y, mo, d = [int(x) for x in iso_s.split('-')]
    return '%d年%d月%d日(%s)' % (y, mo, d, WD[datetime.date(y, mo, d).weekday()])


src = io.open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
by = {e['id']: e for e in events}

built = json.load(io.open('tmp/built_merge_0910.json', encoding='utf-8'))
cands = {c['newid']: c for c in json.load(io.open('tmp/cand_merge_0910.json', encoding='utf-8'))}

added = burned = 0
touched = []
for b in built:
    e = by.get(b['id'])
    if not e:
        continue
    srcurl = cands[b['id']]['urls'][0]
    myurl = (e.get('links') or {}).get('pia') or ''

    # ① 既存の url 空の枠に、既存の links.pia を焼き込む（会場が増える前に）
    for t in e.get('tickets') or []:
        if not t.get('url') and myurl:
            t['url'] = myurl
            burned += 1

    # ② 既存に無い骨格の枠だけ足す。**そのページのURLを焼き込む**
    have = {head(t.get('type')) for t in (e.get('tickets') or [])}
    news = []
    for bt in b.get('tickets') or []:
        if head(bt.get('type')) in have:
            continue
        t = dict(bt)
        t['url'] = bt.get('url') or srcurl
        news.append(t)
    if not news:
        continue
    e.setdefault('tickets', []).extend(news)
    added += len(news)

    # ③ 🚨会場（venue）は**作り直さない**。
    #    ここで union すると、駐車場チケットのように「公演会場ではないページ」の会場名を
    #    ツアーの会場一覧に混ぜてしまう（2026-09-10 id4998 にし阿波の花火で発生）。
    #    直すのは「嘘になるところ」だけ＝**千秋楽(date) と 県 と dateLabel の日付**。
    #    date を伸ばさないと、足した先の公演が来る前にカードが画面から消える
    #    （[[feedback_longrun_event]]＝date は千秋楽）。
    prefs = []
    for t in e.get('tickets') or []:
        bm = re.search(r'（([^（）]*?)\s*(?:R\d+年\s*)?\d{1,2}/\d{1,2}', t.get('type') or '')
        if not bm:
            continue
        for p in re.split(r'[・/／]', bm.group(1)):
            p = p.strip()
            if p and p != '全国' and p not in prefs:
                prefs.append(p)
    # 🚨初日は**今の dateLabel に書いてある初日**から取る。
    #   e['date'] は千秋楽なので、それを初日として使うと会期が縮んで嘘になる
    #   （[[feedback_show_true_dates_not_sellable_range]]）。
    dm = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', e.get('dateLabel') or '')
    cur0 = '%04d-%02d-%02d' % (int(dm.group(1)), int(dm.group(2)), int(dm.group(3))) if dm else None
    d0 = min(x for x in [cur0, e.get('date'), b.get('date')] if x)
    d1 = max(x for x in [e.get('date'), b.get('date')] if x)
    if prefs:
        e['prefecture'] = '・'.join(prefs)
    e['date'] = d1
    e['dateLabel'] = ('%s〜%s %s' % (jp(d0), jp(d1), e.get('prefecture') or '')).strip() if d0 != d1 \
        else ('%s %s' % (jp(d1), e.get('prefecture') or '')).strip()
    touched.append((e['id'], e.get('name', '')[:34], len(news), e['dateLabel'][:52]))

print('足した枠 %d / 既存のurl空に焼き込んだ %d / 触ったエントリ %d件'
      % (added, burned, len(touched)))
for i, n, k, v in touched:
    print('  id=%-5s %-34s ＋%d枠  %s' % (i, n, k, v))

if not APPLY:
    print('\n(--apply で書き込み)')
    sys.exit(0)

arr = json.dumps(events, ensure_ascii=False, indent=2)
io.open('index.html', 'w', encoding='utf-8').write(
    src[:m.start()] + m.group(1) + arr + m.group(3) + src[m.end():])
print('書き込み完了')
