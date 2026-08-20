# -*- coding: utf-8 -*-
"""4789 天皇杯2回戦は33会場あるのに、枠の文言が県名だけで同じ県が複数ある（神奈川4・東京3…）＝
画面でどの試合か分からない。ぴあの生データから会場名を拾って枠名に入れ、枠ごとのURLを付ける。
（[[feedback_same_day_show_time_badge]]＝同じ日に複数あるものは区別できる表記にする
  ／[[feedback_tour_per_ticket_url]]＝会場別URL／[[feedback_dedup_badges_keeps_urls]]＝飛び先が違えば別の売り場）
"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

PREF = {'北海道': '北海道'}
rows = json.load(io.open('tmp/tenno2_raw.json', encoding='utf-8'))
built = json.load(io.open('tmp/built_extra_0820.json', encoding='utf-8'))


def short_pref(p):
    return re.sub(r'(都|府|県)$', '', p or '')


def norm(s):
    """ぴあの全角ローマ字・数字を半角へ（サイトの既存表記に合わせる）。"""
    import unicodedata
    return unicodedata.normalize('NFKC', s or '')


tickets = []
for r in rows:
    if r.get('state') != '受付中':
        continue
    title = r.get('title') or ''
    kind = norm(title.split('／')[0].strip())    # 「一般発売」「一般発売【グループ席・企画券】」等
    # 駐車券は前半でなく公演名側に「駐車券」と書かれている（＜駐車券＞ / 末尾に 駐車券）
    extra = '【駐車券】' if ('駐車' in norm(title) and '駐車' not in kind) else ''
    when = r.get('when') or ''
    # 「～ 2026/8/25(火) 23:59」形
    m = re.search(r'～\s*(\d{4})/(\d+)/(\d+)\([^)]*\)\s*(\d+:\d+)', when.replace('〜', '～'))
    if not m:
        continue
    yy, mm, dd, hhmm = int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4)
    date = '%04d-%02d-%02d' % (yy, mm, dd)
    venue = norm(r.get('venue') or '')
    pref = short_pref(r.get('pref'))
    ev = re.search(r'eventCd=(\d+)', r.get('url') or '')
    url = 'https://t.pia.jp/pia/event/event.do?eventCd=%s' % ev.group(1) if ev else ''
    tickets.append({
        'type': '%s%s（%s 8/26公演 %s）〜%d/%d %s' % (kind, extra, pref, venue, mm, dd, hhmm),
        'date': date,
        'url': url,
    })

for e in built:
    if e['id'] != 4789:
        continue
    e['tickets'] = tickets
    e['venue'] = '全国ツアー（' + '／'.join(
        dict.fromkeys(norm(r['venue']) for r in rows if r.get('state') == '受付中' and r.get('venue'))) + '）'
    print('枠 %d件' % len(tickets))
    for t in tickets:
        print('  -', t['type'], '|', t['url'])

io.open('tmp/built_extra_0820.json', 'w', encoding='utf-8').write(
    json.dumps(built, ensure_ascii=False, indent=1))
