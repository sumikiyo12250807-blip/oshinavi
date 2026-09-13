# -*- coding: utf-8 -*-
"""購入ボタンのAJAX（rakuten_perf_status）の結果から OSHINAVI のエントリを組む（2026-09-13）。

なぜ手で組むか＝この3件は生HTMLに販売枠が1つも出ない形式で、build_rakuten_entries が
「販売枠なし」で落とす。売り状態はAJAXにしか無い（memory reference_rakuten_harvest）。

決まり
  ・買える公演（status=buyable）だけ枠にする
  ・締切は AJAX の sale_end をそのまま使う＝嘘の締切を作らない（memory feedback_no_placeholder_dates）
  ・バッジは完全M/D形＋（県 M/D公演）（memory feedback_badge_date_full_form）
  ・楽天URLは Deep Link に変換（memory feedback_rakuten_deeplink）
  ・配信のみの回は dateLabel の頭に【配信視聴のみ】＝id1904 と同じ形

使い方: python tmp/build_rakuten_perf_0913.py <開始id> [--apply]
出力: tmp/built_rakuten_perf_0913.json
"""
import datetime
import io
import json
import re
import sys
import unicodedata

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_harvest as R  # noqa: E402

START = int(sys.argv[1])
TODAY = '2026-09-13'
PREF = {'東京都': '東京', '神奈川県': '神奈川', '大阪府': '大阪', '京都府': '京都', '北海道': '北海道'}


def pref(s):
    s = s or ''
    return PREF.get(s, re.sub(r'[都道府県]$', '', s))


def md(iso):
    y, m, d = iso.split('-')
    return '%d/%d' % (int(m), int(d))


WD = '月火水木金土日'


def mdlabel(iso):
    """'2026-09-19' → '2026年9月19日(土)'。曜日は実カレンダーから出す（写経しない）。"""
    y, m, d = (int(x) for x in iso.split('-'))
    return '%d年%d月%d日(%s)' % (y, m, d, WD[datetime.date(y, m, d).weekday()])


def endlabel(s):
    """'2026-09-29 19:30' → '〜9/29 19:30'（年が違えば R9年 を付ける）"""
    d, t = s.split(' ')
    y = d.split('-')[0]
    return ('〜%s%s %s' % ('R9年 ' if y == '2027' else '', md(d), t))


src = json.load(io.open('tmp/rakuten_perf_0913.json', encoding='utf-8'))
sweep = {x['url']: x for x in json.load(io.open('tmp/rakuten_presale.json', encoding='utf-8'))['onsale']}

WANT = ('乃木坂46', '櫻坂46', 'バスケットボールリーグ')
out, nid = [], START
for d in src:
    name = d.get('_name') or ''
    if not any(w in name for w in WANT):
        continue
    rows = [r for r in d['rows'] if r.get('status') == 'buyable']
    if not rows:
        print('⏭ 買える公演なし:', name[:34])
        continue
    url = d['url']
    deep = R.deeplink(url)
    g = (sweep.get(url) or {}).get('_genre')
    days = sorted({r['date'] for r in rows})
    prefs = sorted({pref(r['pref']) for r in rows if r.get('pref') and r['pref'] != '全国'})
    venues = sorted({r['venue'] for r in rows if r.get('venue') and r['venue'] != '各会場'})
    streaming = all('視聴' in (r.get('venue') or '') for r in rows)

    # 🚨同じ文言のバッジが並ぶと、別々の売り場が同じものに見える（memory feedback_badge_date_full_form）。
    #   会場が複数あるイベントは、券種名に会場を入れて見分けられるようにする。
    multi = len(venues) > 1
    future = [d for d in days if d >= TODAY]
    tickets = []
    for r in rows:
        p = pref(r['pref']) if r.get('pref') and r['pref'] != '全国' else '・'.join(prefs)
        v = r.get('venue') or ''
        if streaming:
            head = '一般発売【配信視聴】'
        elif v == '各会場':
            # 通し券（シーズンシート等）＝券種名から素直に取る。半角カナは全角へ直す
            nm = re.sub(r'^〔.*?〕\s*', '', r.get('ticket_name') or '').strip()
            nm = unicodedata.normalize('NFKC', nm)
            head = '一般発売【%s】' % re.sub(r'\s*\d{1,2}/\d{1,2}\(.\)〜\d{1,2}/\d{1,2}\(.\)\s*$', '', nm)
        elif multi:
            head = '一般発売【%s】' % v
        else:
            head = '一般発売'
        # 🚨通し券（各会場）は1日ぶんの券ではないので、公演日の欄に「これから残っている会期」を書く。
        #   楽天が返す date は会期の初日（＝もう終わった日）なので、そのまま出すと嘘になる。
        if v == '各会場' and future:
            day = md(future[0]) if len(future) == 1 else '%s〜%s' % (md(future[0]), md(future[-1]))
        else:
            day = md(r['date'])
        tickets.append({
            'type': '%s（%s %s公演）%s' % (head, p, day, endlabel(r['sale_end'])),
            'date': r['sale_end'].split(' ')[0],
            'url': deep,
        })

    # 🚨日付の欄に入れるのは「これから行われる公演」だけ＝もう終わった日は入れない
    #   （memory feedback_show_true_dates_not_sellable_range の2026-09-12項）。
    #   配信のアーカイブだけは例外＝公演自体は済んでいるので実際の公演日を書く（id1904と同じ形）。
    shown = days if streaming else [d for d in days if d >= TODAY]
    if not shown:
        shown = days
    label = '%s〜%s' % (mdlabel(shown[0]), mdlabel(shown[-1])) if len(shown) > 1 else mdlabel(shown[0])
    if streaming:
        label = '【配信視聴のみ】' + label
    e = {
        'id': nid, 'artist': name, 'name': name,
        'date': days[-1],
        'dateLabel': '%s %s %s' % (label, '／'.join(prefs), venues[0] if len(venues) == 1 else '全国ツアー（%s）' % '／'.join(venues)),
        'venue': venues[0] if len(venues) == 1 else '全国ツアー（%s）' % '／'.join(venues),
        'prefecture': '・'.join(prefs),
        'genre': 'new', '_genre': g, '_extraGenres': [],
        'price': None,
        'links': {'rakuten': deep, 'lawson': None, 'pia': None, 'eplus': None},
        'tickets': tickets,
        'verified': True, 'verifiedAt': '2026-09-13',
    }
    out.append(e)
    nid += 1
    print('id%s %s | %s | %s | 枠%d | _genre=%s' % (e['id'], name[:34], e['date'], e['prefecture'], len(tickets), g))
    for t in tickets:
        print('     -', t['type'])

json.dump(out, io.open('tmp/built_rakuten_perf_0913.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('→ tmp/built_rakuten_perf_0913.json （%d件）' % len(out))
