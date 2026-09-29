#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""livePocket 独立ゲート（2026-09-28）

livepocket_harvest / build_livepocket_entries / gate_livepocket_slots / heal_livepocket を
一切使わず、実ページ https://livepocket.jp/e/<id> の生HTMLを自前で読み、登録（投入前の built JSON
または index.html の EVENTS）と突き合わせる。1つでも食い違い・判定不能があれば exit 1。

見る項目（仕様 tmp/x0928e/lp_gate_spec.md の①〜⑦）
  ① entry.date ＝ 最終開催日／dateLabel の初日・最終日（会期の型）・開演時刻
  ② venue・prefecture（正規化して比較）
  ③ 受付の数（販売前/販売中/予定販売枚数終了/販売終了）＝ 登録の枠の数（URLごと）
  ④ 各受付の startDate・date（締切。公演日より後なら公演日。配信は例外）・soldout・saleEnded・type内の発売/締切表記
  ⑤ 最終開催日が今日より前のエントリが無い
  ⑥ 出す側（出店・出展・出演エントリー・案内登録・サークル参加など）の混入が無い
  ⑦ 読めないページ・知らない札・読めない枠表記は「一致」にしない（判定不能として exit 1）

使い方
  python tools/gate_livepocket_indep.py --built tmp/x0928e/built_livepocket.json [--limit 40]
  python tools/gate_livepocket_indep.py --ids 24632,24633        （index.html の id／livePocketのイベントIDも可）
  python tools/gate_livepocket_indep.py                           （index.html の livePocket 由来すべて）
  python tools/gate_livepocket_indep.py --selftest
  オプション: --today YYYY-MM-DD / --sleep 秒(既定2.0・1未満は1に) / --report パス / --html-dir 保存HTMLの置き場
"""
import argparse
import datetime as dt
import html as H
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, 'index.html')
DEFAULT_REPORT = os.path.join(ROOT, 'tmp', 'gate_livepocket_indep_report.txt')
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/128.0 Safari/537.36')

KNOWN_STATUS = ('販売前', '販売中', '予定販売枚数終了', '販売終了')
# 状態の札の横に並ぶ副札（状態ではない）。ここに無い副札は⑦＝判定不能のまま
EXTRA_TAGS = ('ファンクラブチケット',)
# 出す側（出店・出展する人／出演する人／案内を受け取るだけ）の受付
DASU_RE = re.compile(r'出店|出展|出演エントリー|出演者エントリー|出演申込|出演者募集|出演者申込|'
                     r'案内登録|エントリー受付|サークル参加|ブース申込|ブース出')
PREFS = ['北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県', '茨城県', '栃木県', '群馬県',
         '埼玉県', '千葉県', '東京都', '神奈川県', '新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県',
         '岐阜県', '静岡県', '愛知県', '三重県', '滋賀県', '京都府', '大阪府', '兵庫県', '奈良県', '和歌山県',
         '鳥取県', '島根県', '岡山県', '広島県', '山口県', '徳島県', '香川県', '愛媛県', '高知県', '福岡県',
         '佐賀県', '長崎県', '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県']


def short_pref(p):
    if not p:
        return ''
    p = p.strip()
    if p == '北海道' or p not in PREFS:
        return p   # すでに短い形（京都・東京…）はそのまま＝「京都」の「都」を削らない
    return p[:-1]


def nfkc(s):
    return unicodedata.normalize('NFKC', s or '')


def norm_name(s):
    s = nfkc(s).lower()
    s = re.sub(r'[\s　]+', '', s)
    s = s.replace('〜', '~').replace('～', '~')
    return s


def strip_tags(s):
    s = re.sub(r'<!--.*?-->', ' ', s, flags=re.S)
    s = re.sub(r'<br\s*/?>', ' ', s, flags=re.I)
    s = re.sub(r'<(?:[^>"\']|"[^"]*"|\'[^\']*\')*>', ' ', s)   # 属性値の中の > にだまされない
    return re.sub(r'\s+', ' ', H.unescape(s)).strip()


# ---------------------------------------------------------------- 取得
class FetchError(Exception):
    pass


def event_id_of(url):
    m = re.search(r'livepocket\.jp/e/([^/?#]+)', url or '')
    return m.group(1) if m else None


_last_fetch = [0.0]


def fetch(url, sleep, html_dir=None):
    eid = event_id_of(url)
    if html_dir and eid:
        p = os.path.join(html_dir, eid + '.html')
        if os.path.exists(p) and os.path.getsize(p) > 5000:
            with open(p, encoding='utf-8') as f:
                return f.read()
    waits = [0, 90, 180]
    last_err = ''
    for w in waits:
        if w:
            print('   … 取得を止められた（%s）。%d秒待ってやり直し' % (last_err, w), flush=True)
            time.sleep(w)
        gap = time.time() - _last_fetch[0]
        if gap < sleep:
            time.sleep(sleep - gap)
        req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'text/html',
                                                   'Accept-Language': 'ja'})
        try:
            r = urllib.request.urlopen(req, timeout=40)
            body = r.read()
            status = r.status
            waf = r.headers.get('x-amzn-waf-action')
        except urllib.error.HTTPError as ex:
            _last_fetch[0] = time.time()
            if ex.code in (404, 410):
                raise FetchError('ページが無い（HTTP %d）' % ex.code)
            last_err = 'HTTP %d' % ex.code
            continue
        except Exception as ex:  # noqa
            _last_fetch[0] = time.time()
            last_err = str(ex)[:80]
            continue
        _last_fetch[0] = time.time()
        if status == 200 and not waf and len(body) > 5000:
            text = body.decode('utf-8', 'replace')
            if html_dir and eid:
                os.makedirs(html_dir, exist_ok=True)
                with open(os.path.join(html_dir, eid + '.html'), 'w', encoding='utf-8') as f:
                    f.write(text)
            return text
        last_err = 'HTTP %s%s・%dバイト' % (status, '・WAF ' + waf if waf else '', len(body))
    raise FetchError('取得できない（%s）' % last_err)


# ---------------------------------------------------------------- 実ページを読む
DATE_RE = re.compile(r'(?:(\d{4})年)?(\d{1,2})月(\d{1,2})日')
DT_RE = re.compile(r'(\d{4})年(\d{1,2})月(\d{1,2})日(?:\s*[\(（][^)）]*[\)）])?\s*(\d{1,2}):(\d{2})')


def parse_dates_text(txt):
    out = []
    year = None
    for m in DATE_RE.finditer(txt):
        if m.group(1):
            year = int(m.group(1))
        if year is None:
            return None
        out.append(dt.date(year, int(m.group(2)), int(m.group(3))))
    return out


def parse_page(raw):
    """生HTML → dict。読めなければ 'err' に理由。"""
    pg = {'err': None}
    h = re.sub(r'<(script)(?![^>]*ld\+json)[^>]*>.*?</script>', ' ', raw, flags=re.S | re.I)
    h = re.sub(r'<(style|svg|noscript)[^>]*>.*?</\1>', ' ', h, flags=re.S | re.I)
    h = re.sub(r'<!--.*?-->', ' ', h, flags=re.S)

    # JSON-LD（補助）
    ld = None
    m = re.search(r'<script[^>]*ld\+json[^>]*>(.*?)</script>', raw, re.S)
    if m:
        try:
            ld = json.loads(m.group(1))
        except Exception:
            ld = None
    if isinstance(ld, list):
        ld = next((x for x in ld if isinstance(x, dict) and x.get('@type') == 'Event'), None)
    pg['ld'] = ld
    h = re.sub(r'<script[^>]*>.*?</script>', ' ', h, flags=re.S | re.I)

    # 概要（開催日・時間・会場）
    i0 = None
    for mm in re.finditer(r'<dt[^>]*>(?:(?!</dt>).)*?開催日(?:(?!</dt>).)*?</dt>', h, re.S):
        i0 = mm.start()
        break
    if i0 is None:
        pg['err'] = '概要（開催日）が読めない'
        return pg
    ends = [x for x in (h.find('<h2', i0), h.find('<dialog', i0), h.find('<section', i0)) if x > 0]
    ov = h[i0:min(ends) if ends else i0 + 20000]
    blocks = {}
    raw_blocks = {}
    order = []
    for part in re.split(r'<dt\b', ov)[1:]:
        title = strip_tags(part.split('</dt>', 1)[0].split('>', 1)[-1]) if '</dt>' in part else ''
        rest = part.split('</dt>', 1)[1] if '</dt>' in part else ''
        if title and title not in blocks:
            blocks[title] = strip_tags(rest)
            raw_blocks[title] = rest
            order.append(title)
    pg['blocks'] = blocks
    kaisai = blocks.get('開催日', '')
    dates = parse_dates_text(kaisai)
    if not dates:
        pg['err'] = '開催日が読めない（%s）' % kaisai[:40]
        return pg
    pg['dates'] = dates
    pg['first'], pg['last'] = min(dates), max(dates)
    pg['range'] = ('〜' in kaisai or '～' in kaisai) and pg['first'] != pg['last']
    if ld and isinstance(ld, dict):
        try:
            ls = dt.date.fromisoformat(str(ld.get('startDate', ''))[:10])
            le = dt.date.fromisoformat(str(ld.get('endDate', ''))[:10])
            if (ls, le) != (pg['first'], pg['last']):
                pg['err'] = 'ページ内で開催日が食い違う（概要 %s〜%s／構造化データ %s〜%s）' % (
                    pg['first'], pg['last'], ls, le)
                return pg
        except ValueError:
            pass
    # 時刻（時間の欄＝開演/START/開場/OPEN/販売時間 など）
    # 「時間」の欄から「会場」の欄の手前まで（中の小見出し＝開演時間/START/イベント開始/開演日時…）
    tkeys = []
    if '時間' in order:
        for k in order[order.index('時間'):]:
            if k in ('会場', '出演者', '販売元'):
                break
            tkeys.append(k)
    time_txt = ' '.join(nfkc(blocks[k]) for k in tkeys)
    pg['times'] = sorted(set('%d:%s' % (int(a), b) for a, b in re.findall(r'(\d{1,2}):(\d{2})', time_txt)))
    kaien = []
    for k in tkeys:
        if re.search(r'開演|START|開始', k, re.I):
            mm = re.search(r'(\d{1,2}):(\d{2})', nfkc(blocks.get(k, '')))
            if mm:
                kaien.append('%d:%s' % (int(mm.group(1)), mm.group(2)))
    pg['kaien'] = kaien
    # 会場
    vraw = raw_blocks.get('会場')
    if vraw is None:
        pg['err'] = '会場の欄が無い'
        return pg
    mm = re.search(r'<dd[^>]*>(.*?)(?:<span|<br|<div|</dd>)', vraw, re.S)
    line = strip_tags(mm.group(1)) if mm else ''
    pref = None
    vname = line
    mm = re.match(r'^(.*?)\s*[\(（]\s*([^()（）]+?)\s*[\)）]\s*$', line)
    if mm and mm.group(2) in PREFS:
        vname, pref = mm.group(1).strip(), mm.group(2)
    pg['venue'] = vname
    pg['pref'] = short_pref(pref) if pref else ''
    pg['ld_venue'] = ((ld or {}).get('location') or {}).get('name') if isinstance(ld, dict) else None
    # メタ説明の「会場(県)」＝補助
    md = re.search(r'<meta[^>]+name=.description.[^>]+content="([^"]*)"', raw)
    pg['meta_desc'] = H.unescape(md.group(1)) if md else ''

    # 受付・チケット情報
    mh = re.search(r'<h2[^>]*>\s*受付・チケット情報\s*</h2>', h)
    if not mh:
        pg['err'] = '受付・チケット情報の欄が無い'
        return pg
    j = h.find('<h2', mh.end())
    sec = h[mh.end(): j if j > 0 else len(h)]
    items = re.split(r'<li\b[^>]*event-detail-ticket__item[^>]*>', sec)[1:]
    recs = []
    for it in items:
        k3 = it.find('<h3')
        if k3 < 0:
            pg['err'] = '受付の見出しが読めない'
            return pg
        status = strip_tags(it[:k3])
        # 札の横に付く副札（例「販売中 ファンクラブチケット」）＝状態の札が1つだけ・副札が既知なら状態として読む
        toks = status.split()
        known = [x for x in toks if x in KNOWN_STATUS]
        extra = [x for x in toks if x not in KNOWN_STATUS]
        subtags = []
        if len(known) == 1 and extra and all(x in EXTRA_TAGS for x in extra):
            status, subtags = known[0], extra
        h3 = it[k3: it.find('</h3>', k3)]
        lab = re.search(r'<span[^>]*>(.*?)</span>', h3, re.S)
        label = strip_tags(lab.group(1)) if lab else ''
        title = strip_tags(re.sub(r'<span[^>]*>.*?</span>', ' ', h3.split('>', 1)[1], count=1, flags=re.S))
        mp = re.search(r'販売受付期間\s*</dt>\s*<dd[^>]*>(.*?)</dd>', it, re.S)
        period = strip_tags(mp.group(1)) if mp else ''
        dts = [dt.datetime(int(a), int(b), int(c), int(d), int(e)) for a, b, c, d, e in DT_RE.findall(period)]
        start = end = None
        if '〜' in period or '～' in period:
            left, right = re.split(r'[〜～]', period, maxsplit=1)
            ls = DT_RE.search(left)
            rs = DT_RE.search(right)
            if ls:
                start = dt.datetime(*map(int, ls.groups()))
            if rs:
                end = dt.datetime(*map(int, rs.groups()))
        cards = [strip_tags(c) for c in re.findall(r'<h4[^>]*>(.*?)</h4>', it, re.S)]
        recs.append({'status': status, 'subtags': subtags, 'label': label, 'title': title, 'period': period,
                     'start': start, 'end': end, 'cards': cards, 'n_dt': len(dts),
                     'text': strip_tags(it)})
    pg['recs'] = recs
    return pg


# ---------------------------------------------------------------- 登録の枠表記を読む
TYPE_RE = re.compile(
    r'^(?P<name>.*?)(?P<hai>（配信）)?'
    r'（(?:(?P<pref>[^\s（）]+) )?(?P<r>R\d+年 )?'
    r'(?P<show>\d{1,2}/\d{1,2}(?: \d{1,2}:\d{2})?公演|\d{1,2}/\d{1,2}〜\d{1,2}/\d{1,2})）'
    r'(?:(?P<st>\d{1,2}/\d{1,2} \d{1,2}:\d{2})発売)?'
    r'〜(?P<en>\d{1,2}/\d{1,2} \d{1,2}:\d{2})$')


def parse_type(s):
    m = TYPE_RE.match(s or '')
    if not m:
        return None
    g = m.groupdict()
    return {'name': g['name'].strip(), 'haishin': bool(g['hai']), 'pref': g['pref'] or '',
            'show': g['show'], 'start': g['st'], 'end': g['en']}


def md_hm(d):
    return '%d/%d %d:%02d' % (d.month, d.day, d.hour, d.minute)


def md_key(s):
    m = re.match(r'(\d{1,2})/(\d{1,2}) (\d{1,2}):(\d{2})$', s or '')
    return tuple(int(x) for x in m.groups()) if m else None


def dkey(d):
    return (d.month, d.day, d.hour, d.minute)


def is_dasu(title, cards=()):
    if DASU_RE.search(nfkc(title)):
        return True
    return bool(cards) and all(DASU_RE.search(nfkc(c)) for c in cards)


def is_haishin_rec(rec):
    return '配信' in rec['title'] or any('配信' in c for c in rec['cards'])


STREAM_ANY = re.compile(r'配信(?!なし|無し)|視聴(?!覚)|アーカイブ')
ONLINE_V = re.compile(r'^\s*(オンライン|配信|Zoom|ツイキャス|YouTube|ONLINE|Online)', re.I)


def after_show_stream_rec(pg, r, today):
    """🆕2026-09-30 公演日が過ぎても載せ続ける受付か（ZAIKOのスタリオン＝配信は公演日の後も売っている）。
    配信の受付（受付名・券種名に配信/視聴/アーカイブ、または会場がオンライン）で、締切が今日以降。
    ビルダー（build_livepocket_entries）は、公演日が過ぎたページからこの受付だけを出す。"""
    if r.get('end') is None or r['end'].date() < today:
        return False
    return bool(STREAM_ANY.search(nfkc(r['title'])) or any(STREAM_ANY.search(nfkc(c)) for c in r['cards'])
                or ONLINE_V.search(pg.get('venue') or ''))


def live_after_show(pg, today):
    """公演日が過ぎたページに、まだ買える配信の受付（販売中・販売前）があるか。"""
    return any(r['status'] in ('販売中', '販売前') and after_show_stream_rec(pg, r, today) for r in pg.get('recs') or [])


# ---------------------------------------------------------------- 突き合わせ
def check_entry(e, pages, today):
    """pages: {url: parse_page結果 or {'err':...}}。戻り値 (issues, undecidable, n_slots, n_ok_slots)
    issues/undecidable の各要素 = (項目, 登録の値, 実ページの値, URL)"""
    iss, und = [], []
    link = (e.get('links') or {}).get('livepocket')
    tickets = e.get('tickets') or []
    by_url = {}
    for t in tickets:
        by_url.setdefault(t.get('url') or link, []).append(t)
    if link and link not in by_url:
        by_url[link] = []
    ok_slots = 0
    for u, pg in pages.items():
        if pg.get('err'):
            und.append(('判定不能（ページ）', '', pg['err'], u))
    good = {u: p for u, p in pages.items() if not p.get('err')}

    # ⑥ 出す側（エントリ名）
    for k in ('name', 'artist'):
        if DASU_RE.search(nfkc(e.get(k) or '')) and re.search(r'募集|申込|エントリー|登録', nfkc(e.get(k) or '')):
            iss.append(('⑥出す側の混入（%s）' % k, e.get(k), '出店/出展/出演者募集などの受付', link))

    # ① 開催日
    if good:
        firsts = [p['first'] for p in good.values()]
        lasts = [p['last'] for p in good.values()]
        first, last = min(firsts), max(lasts)
        if e.get('date') != last.isoformat():
            iss.append(('①date（最終開催日）', e.get('date'), last.isoformat(), link))
        # 🆕2026-09-30 見出しの後ろの「（配信は M月D日(曜) HH:MMまで）」は視聴の終わり＝会期でも開演でもない
        #   （build_livepocket_entries の stream_label）。会期・開演時刻の突き合わせからは外す。
        lab = re.sub(r'（配信は[^（）]*まで）$', '', e.get('dateLabel') or '')
        ld = parse_dates_text(lab) or []
        if not ld:
            und.append(('判定不能（dateLabelが読めない）', lab, '', link))
        else:
            if ld[0] != first:
                iss.append(('①dateLabel初日', lab, first.isoformat(), link))
            if ld[-1] != last:
                iss.append(('①dateLabel最終日', lab, last.isoformat(), link))
            multi = first != last
            if multi and len(ld) < 2:
                iss.append(('①会期の型（複数日なのに1日表記）', lab, '%s〜%s' % (first, last), link))
            if not multi and len(ld) > 1 and ld[0] != ld[-1]:
                iss.append(('①会期の型（1日なのに期間表記）', lab, first.isoformat(), link))
            lt = ['%d:%s' % (int(a), b) for a, b in re.findall(r'(\d{1,2}):(\d{2})', nfkc(lab))]
            pmain = good.get(link) or next(iter(good.values()))
            if lt:
                for x in lt:
                    if x not in pmain['times']:
                        iss.append(('①開演時刻', lab, '・'.join(pmain['times']) or '（時刻なし）', link))
            elif pmain['kaien'] and not multi:
                iss.append(('①開演時刻の欠落', lab, '開演 ' + '・'.join(pmain['kaien']), link))
        # ③' 日付別ページを畳んだエントリの「ページ丸ごと落ち」
        #   どのページも同じ会期（複数日）を名乗り、受付名に「10/25（日）」の形で自分の日を持つ型だけ見る。
        #   会期のうちどのページの日でもない日＝そのページが登録に無い（定休日なら人が確かめる）
        if len(good) >= 2 and all(p['first'] == first and p['last'] == last for p in good.values()) and first != last:
            days = set()
            ok_type = True
            for p in good.values():
                dd = None
                for r in p['recs']:
                    mm = re.search(r'(\d{1,2})/(\d{1,2})\s*[（(]', nfkc(r['title']))
                    if mm:
                        for y in (first.year, last.year):
                            try:
                                c = dt.date(y, int(mm.group(1)), int(mm.group(2)))
                            except ValueError:
                                continue
                            if first <= c <= last:
                                dd = c
                                break
                        break
                if dd is None:
                    ok_type = False
                    break
                days.add(dd)
            if ok_type:
                miss = []
                d = first
                while d <= last:
                    if d not in days:
                        miss.append('%d/%d' % (d.month, d.day))
                    d += dt.timedelta(days=1)
                if miss:
                    iss.append(('③畳んだ会期にページの無い日（日付別ページの落ち）', '%dページ' % len(good),
                                '会期 %s〜%s のうち %s のページが登録に無い' % (first, last, '・'.join(miss)), link))
        # ⑤ 過去
        # 🆕2026-09-30 公演日が過ぎても、まだ買える配信の受付があるページは「終わっている」と言わない
        #   （ZAIKOのスタリオン＝配信中なのに「公演が終わった」扱いで捨てた）
        stream_alive = last < today and any(live_after_show(p, today) for p in good.values())
        if last < today and not stream_alive:
            iss.append(('⑤公演が終わっている', e.get('date'), '最終開催日 %s < 今日 %s' % (last, today), link))
        if e.get('date') and e['date'] < today.isoformat() and not stream_alive:
            iss.append(('⑤登録の公演日が過去', e.get('date'), '今日 %s' % today, link))

    # ② 会場・県（主ページ）
    pm = good.get(link)
    if pm:
        rv = e.get('venue') or ''
        if norm_name(rv) not in (norm_name(pm['venue']), norm_name(pm.get('ld_venue') or '')):
            iss.append(('②venue', rv, pm['venue'], link))
        rp = e.get('prefecture') or ''
        if short_pref(rp) != pm['pref']:
            iss.append(('②prefecture', rp, pm['pref'] or '（ページに県なし）', link))

    # ③④⑥ 受付ごと
    for u, ts in by_url.items():
        pg = good.get(u)
        if not pg:
            continue
        last = pg['last']
        recs = []
        for r in pg['recs']:
            if r['status'] not in KNOWN_STATUS:
                und.append(('判定不能（知らない札）', '', '%s「%s」' % (r['status'] or '（札なし）', r['title']), u))
                continue
            if r['end'] is None:
                und.append(('判定不能（受付期間が読めない）', '', '%s「%s」' % (r['period'] or '（空）', r['title']), u))
                continue
            if r['status'] == '販売前' and r['start'] is None:
                und.append(('判定不能（販売前なのに開始日時が無い）', '', r['period'], u))
                continue
            if last < today and not after_show_stream_rec(pg, r, today):
                continue   # 🆕2026-09-30 公演日が過ぎたページは、締切が今日以降の配信の受付だけを載せる（ビルダーと同じ線）
            r = dict(r)
            r['dasu'] = is_dasu(r['title'], r['cards'])
            recs.append(r)
        parsed = []
        for t in ts:
            pt = parse_type(t.get('type'))
            if pt is None:
                und.append(('判定不能（枠の表記が読めない）', t.get('type'), '', u))
                continue
            parsed.append((t, pt))
        # 対応づけ：締切(M/D H:MM)＋名前（前方一致）
        def reg_state(t):
            return ('販売終了' if t.get('saleEnded') else '予定販売枚数終了' if t.get('soldout')
                    else '販売前' if t.get('startDate') else '販売中')

        used = set()
        pairs = []
        rest = []
        for t, pt in parsed:
            cand = [i for i, r in enumerate(recs) if i not in used and dkey(r['end']) == md_key(pt['end'])]
            nm = norm_name(pt['name'])
            best = [i for i in cand if norm_name(recs[i]['title']).startswith(nm) or nm.startswith(norm_name(recs[i]['title']))
                    or any(norm_name(c).startswith(nm) for c in recs[i]['cards'])]
            # 同名・同締切が複数あるときは、状態の合うものを先に（取り違えで余計に鳴らさない）
            best.sort(key=lambda i: recs[i]['status'] != reg_state(t))
            pick = best[0] if best else (cand[0] if len(cand) == 1 and not nm else None)
            if pick is None and len(cand) == 1:
                pick = cand[0]
                iss.append(('④枠の名前', t.get('type'), recs[pick]['title'], u))
            if pick is None:
                rest.append((t, pt))
                continue
            used.add(pick)
            pairs.append((t, pt, recs[pick]))
        # 締切ずれの対応づけ（名前だけ一致）
        for t, pt in rest:
            nm = norm_name(pt['name'])
            cand = [i for i, r in enumerate(recs) if i not in used and not r['dasu'] and
                    (norm_name(r['title']).startswith(nm) or nm.startswith(norm_name(r['title'])))]
            if cand:
                i = cand[0]
                used.add(i)
                iss.append(('④締切（枠の表記）', t.get('type'), '〜' + md_hm(recs[i]['end']), u))
                pairs.append((t, pt, recs[i]))
            else:
                iss.append(('③実ページに無い枠（増えている）', t.get('type'), '該当する受付なし', u))
        for i, r in enumerate(recs):
            if i in used:
                continue
            if r['dasu']:
                continue  # 出す側＝載せない（数から外す）
            iss.append(('③受付の欠落（登録に無い）', '', '[%s] %s %s' % (r['status'], r['title'], r['period']), u))
        # ③ 状態別の数
        cnt_pg, cnt_rg = {}, {}
        for r in recs:
            if not r['dasu']:
                cnt_pg[r['status']] = cnt_pg.get(r['status'], 0) + 1
        for t, pt in parsed:
            st = ('販売終了' if t.get('saleEnded') else '予定販売枚数終了' if t.get('soldout')
                  else '販売前' if t.get('startDate') else '販売中')
            cnt_rg[st] = cnt_rg.get(st, 0) + 1
        if cnt_pg != cnt_rg:
            iss.append(('③状態別の数', json.dumps(cnt_rg, ensure_ascii=False), json.dumps(cnt_pg, ensure_ascii=False), u))
        # ④ 各枠
        for t, pt, r in pairs:
            n_before = len(iss)
            typ = t.get('type')
            if r['dasu'] or DASU_RE.search(nfkc(pt['name'])):
                iss.append(('⑥出す側の受付が載っている', typ, r['title'], u))
            hai = is_haishin_rec(r) or pt['haishin']
            endd = r['end'].date()
            exp = endd if (hai or endd <= last) else last
            allowed = {exp.isoformat()}
            if hai:
                allowed.add(min(endd, last).isoformat())
            if t.get('date') not in allowed:
                iss.append(('④date（締切）', '%s（%s）' % (t.get('date'), typ),
                            '%s（受付終了 %s・最終開催日 %s）' % ('/'.join(sorted(allowed)), r['end'].strftime('%Y-%m-%d %H:%M'), last), u))
            st = r['status']
            if st == '販売前':
                if t.get('startDate') != r['start'].date().isoformat():
                    iss.append(('④startDate（発売日）', t.get('startDate'), r['start'].strftime('%Y-%m-%d %H:%M'), u))
                if md_key(pt['start'] or '') != dkey(r['start']):
                    iss.append(('④枠の発売表記', typ, md_hm(r['start']) + '発売', u))
            else:
                if t.get('startDate'):
                    iss.append(('④startDate（%sなのに発売日あり）' % st, t.get('startDate'), st, u))
                if pt['start']:
                    iss.append(('④枠の発売表記（%sなのに発売あり）' % st, typ, st, u))
            want_so = st in ('予定販売枚数終了', '販売終了')
            want_se = st == '販売終了'
            if bool(t.get('soldout')) != want_so:
                iss.append(('④soldout', t.get('soldout'), '%s（%s）' % (want_so, st), u))
            if bool(t.get('saleEnded')) != want_se:
                iss.append(('④saleEnded', t.get('saleEnded'), '%s（%s）' % (want_se, st), u))
            # 枠の公演表記（県・公演日）
            if pt['pref'] and short_pref(pt['pref']) != short_pref(e.get('prefecture') or ''):
                iss.append(('②枠の県', typ, e.get('prefecture'), u))
            sm = re.match(r'(\d{1,2})/(\d{1,2})(?: (\d{1,2}:\d{2}))?公演$', pt['show'])
            if sm:
                if (int(sm.group(1)), int(sm.group(2))) != (pg['first'].month, pg['first'].day) or pg['first'] != pg['last']:
                    iss.append(('①枠の公演日', typ, '%s〜%s' % (pg['first'], pg['last']), u))
                shm = sm.group(3) and '%d:%s' % (int(sm.group(3).split(':')[0]), sm.group(3).split(':')[1])
                if shm and shm not in pg['times']:   # 「09:20」と「9:20」を同じに
                    iss.append(('①枠の開演時刻', typ, '・'.join(pg['times']) or '（時刻なし）', u))
            else:
                a, b = pt['show'].split('〜')
                fa = '%d/%d' % (pg['first'].month, pg['first'].day)
                fb = '%d/%d' % (pg['last'].month, pg['last'].day)
                if (a, b) != (fa, fb):
                    iss.append(('①枠の会期', typ, '%s〜%s' % (fa, fb), u))
            if len(iss) == n_before:
                ok_slots += 1
    return iss, und, len(tickets), ok_slots


# ---------------------------------------------------------------- 入力
def load_index_events():
    with open(INDEX, encoding='utf-8') as f:
        src = f.read()
    i = src.index('  const EVENTS = [')
    arr, _ = json.JSONDecoder().raw_decode(src[i + len('  const EVENTS = '):])
    return arr


def is_lp(e):
    return bool((e.get('links') or {}).get('livepocket'))


def label_of(e):
    eid = event_id_of((e.get('links') or {}).get('livepocket'))
    head = ('id %s ' % e['id']) if e.get('id') is not None else ''
    return '%s%s %s' % (head, eid, (e.get('name') or '')[:40])


def run(entries, today, sleep, report, html_dir):
    all_issues = []
    n_ok = n_bad = n_und = 0
    slots_all = slots_ok = 0
    cache = {}
    for k, e in enumerate(entries, 1):
        link = (e.get('links') or {}).get('livepocket')
        urls = []
        for u in [link] + [t.get('url') or link for t in (e.get('tickets') or [])]:
            if u and u not in urls:
                urls.append(u)
        pages = {}
        for u in urls:
            if u not in cache:
                try:
                    cache[u] = parse_page(fetch(u, sleep, html_dir))
                except FetchError as ex:
                    cache[u] = {'err': str(ex)}
            pages[u] = cache[u]
        iss, und, ns, nok = check_entry(e, pages, today)
        slots_all += ns
        if und:
            n_und += 1
        elif iss:
            n_bad += 1
        else:
            n_ok += 1
            slots_ok += nok
        if not und:
            pass
        mark = '判定不能' if und else ('🚨' if iss else '一致')
        print('[%d/%d] %s … %s' % (k, len(entries), label_of(e), mark), flush=True)
        for x in und + iss:
            all_issues.append((label_of(e),) + x)
    lines = ['livePocket 独立ゲート 報告（%s・今日=%s）' % (dt.datetime.now().strftime('%Y-%m-%d %H:%M'), today), '']
    for lab, item, reg, pgv, u in all_issues:
        lines.append('🚨 %s' % lab)
        lines.append('   項目: %s' % item)
        lines.append('   登録: %s' % reg)
        lines.append('   実ページ: %s' % pgv)
        lines.append('   URL: %s' % u)
    lines.append('')
    lines.append('一致 %d件・食い違い %d件・判定不能 %d件 ／ 全 %d件' % (n_ok, n_bad, n_und, len(entries)))
    lines.append('照合できた件 %d/%d件・照合できた枠（一致した件の枠）%d/%d枠' % (
        n_ok + n_bad, len(entries), slots_ok, slots_all))
    text = '\n'.join(lines) + '\n'
    if report:
        os.makedirs(os.path.dirname(os.path.abspath(report)), exist_ok=True)
        with open(report, 'w', encoding='utf-8') as f:
            f.write(text)
    print('\n'.join(lines[-2:]))
    if report:
        print('報告: %s' % report)
    return 0 if (n_bad == 0 and n_und == 0) else 1


# ---------------------------------------------------------------- 自己テスト
def _mk_page(first, last, time_label, time_val, venue, pref, recs, ld=True):
    def jd(d):
        w = '月火水木金土日'[d.weekday()]
        return '%d年%d月%d日(%s)' % (d.year, d.month, d.day, w)
    kaisai = jd(first) if first == last else jd(first) + '〜' + jd(last)
    tb = ''
    if time_label:
        tb = ('<div><dt class="t"><span>時間</span></dt><dd class="d"><dl><dt>%s</dt><dd>%s</dd></dl></dd></div>'
              % (time_label, time_val))
    lis = ''
    for st, title, s, en, card in recs:
        per = ('%s %s' % (jd(s), s.strftime('%H:%M')) if s else '') + '<br />〜%s %s' % (jd(en), en.strftime('%H:%M'))
        lis += ('<li class="event-detail-ticket__item js-toggle"><a><div><span class="tag">%s</span></div>'
                '<h3><span class="label-order">先着</span> %s </h3><dl><dt>販売受付期間</dt><dd>%s</dd></dl></a>'
                '<div><section><h4>%s</h4><span>%s</span></section></div></li>' % (st, title, per, card, st))
    ldj = ''
    if ld:
        ldj = ('<script type="application/ld+json">{"@type":"Event","startDate":"%sT00:00","endDate":"%sT00:00",'
               '"location":{"@type":"Place","name":"%s"}}</script>' % (first, last, venue))
    return ('<html><head>%s</head><body>' % ldj + ' ' * 5000 +
            '<dl><div><dt><span>開催日</span></dt><dd>%s</dd></div>%s'
            '<div><dt><span>会場</span></dt><dd>%s (%s)<span>住所</span></dd></div></dl>'
            '<h2 class="heading02">詳細</h2><p>本文</p>'
            '<section><h2 class="heading02">受付・チケット情報</h2><ul>%s</ul></section>'
            '<h2>お問い合わせ</h2></body></html>' % (kaisai, tb, venue, pref, lis))


def selftest():
    D = dt.datetime
    today = dt.date(2026, 9, 28)
    url = 'https://livepocket.jp/e/test1'
    recs = [
        ('販売前', '先行受付', D(2026, 10, 1, 12, 0), D(2026, 10, 20, 23, 59), '一般'),
        ('販売中', '先着販売受付', D(2026, 9, 20, 10, 0), D(2026, 10, 25, 19, 0), '一般'),
        ('予定販売枚数終了', 'Sチケット', D(2026, 9, 20, 10, 0), D(2026, 10, 25, 19, 0), 'S'),
        ('販売終了', '抽選受付', D(2026, 9, 1, 10, 0), D(2026, 9, 20, 23, 59), '一般'),
        ('販売中', '出店者申込受付', D(2026, 9, 1, 10, 0), D(2026, 10, 20, 23, 59), 'ブース'),
    ]
    page = _mk_page(dt.date(2026, 10, 25), dt.date(2026, 10, 25), '開演時間', '19:00', '渋谷ホール', '東京都', recs)
    good = {
        'name': 'テスト公演', 'artist': 'テスト', 'date': '2026-10-25', 'dateLabel': '2026年10月25日(日) 19:00開演',
        'venue': '渋谷ホール', 'prefecture': '東京', 'links': {'livepocket': url},
        'tickets': [
            {'type': '先行受付（東京 10/25 19:00公演）10/1 12:00発売〜10/20 23:59', 'date': '2026-10-20', 'startDate': '2026-10-01', 'url': url},
            {'type': '先着販売受付（東京 10/25 19:00公演）〜10/25 19:00', 'date': '2026-10-25', 'url': url},
            {'type': 'Sチケット（東京 10/25 19:00公演）〜10/25 19:00', 'date': '2026-10-25', 'soldout': True, 'url': url},
            {'type': '抽選受付（東京 10/25 19:00公演）〜9/20 23:59', 'date': '2026-09-20', 'soldout': True, 'saleEnded': True, 'url': url},
        ]}
    pg = parse_page(page)
    assert not pg['err'], pg['err']
    fails = 0

    def run1(name, e, p=pg, td=today, want=True, key=None):
        nonlocal fails
        iss, und, _, _ = check_entry(e, {url: p}, td)
        got = iss + und
        hit = bool(got) if key is None else any(key in x[0] for x in got)
        ok = hit if want else not got
        print('  %s %s → %s' % ('OK ' if ok else 'NG ', name, '; '.join(x[0] for x in got) or '一致'))
        if not ok:
            fails += 1

    import copy
    run1('正しい登録は鳴らない', good, want=False)
    m = copy.deepcopy(good); m['tickets'][0]['date'] = '2026-10-21'
    run1('締切ずれ（date+1日）', m, key='④date')
    m = copy.deepcopy(good); m['tickets'][1]['type'] = '先着販売受付（東京 10/25 19:00公演）〜10/24 19:00'
    run1('締切ずれ（枠の表記）', m, key='締切')
    m = copy.deepcopy(good); del m['tickets'][2]['soldout']
    run1('売切の印の欠落', m, key='soldout')
    m = copy.deepcopy(good); del m['tickets'][3]['saleEnded']
    run1('販売終了の印の欠落', m, key='saleEnded')
    m = copy.deepcopy(good); del m['tickets'][1]
    run1('受付1つ欠落', m, key='③受付の欠落')
    m = copy.deepcopy(good); m['prefecture'] = '神奈川'
    run1('県違い', m, key='②prefecture')
    m = copy.deepcopy(good); m['venue'] = '新宿ホール'
    run1('会場違い', m, key='②venue')
    m = copy.deepcopy(good); del m['tickets'][0]['startDate']
    run1('startDate欠落', m, key='startDate')
    m = copy.deepcopy(good); m['tickets'][1]['startDate'] = '2026-09-20'
    run1('販売中にstartDate', m, key='startDate')
    run1('過去公演（今日が公演日の翌日）', good, td=dt.date(2026, 10, 26), key='⑤')
    m = copy.deepcopy(good); m['date'] = '2026-09-27'; m['dateLabel'] = '2026年9月27日(日) 19:00開演'
    run1('公演日を過去に書き換え', m, key='①date')
    m = copy.deepcopy(good); m['tickets'].append(
        {'type': '出店者申込受付（東京 10/25 19:00公演）〜10/20 23:59', 'date': '2026-10-20', 'url': url})
    run1('出す側の混入', m, key='⑥')
    m = copy.deepcopy(good); m['dateLabel'] = '2026年10月25日(日) 18:00開演'
    run1('開演時刻違い', m, key='①開演時刻')
    m = copy.deepcopy(good); m['tickets'].append(copy.deepcopy(m['tickets'][1]))
    run1('枠が増えている', m, key='③')
    bad = _mk_page(dt.date(2026, 10, 25), dt.date(2026, 10, 25), '開演時間', '19:00', '渋谷ホール', '東京都',
                   [('一時停止中',) + recs[1][1:]] + recs[:1] + recs[2:])
    run1('知らない札', good, p=parse_page(bad), key='判定不能')
    run1('読めないページ（WAF）', good, p=parse_page('<html>challenge</html>'), key='判定不能')
    # 複数日・配信
    url2 = url
    page2 = _mk_page(dt.date(2026, 10, 3), dt.date(2026, 10, 4), None, None, 'オンライン', '東京都',
                     [('販売中', '先着販売受付', D(2026, 9, 20, 10, 0), D(2026, 10, 10, 20, 0), '配信チケット')])
    e2 = {'name': 'x', 'date': '2026-10-04', 'dateLabel': '2026年10月3日(土)〜2026年10月4日(日)', 'venue': 'オンライン',
          'prefecture': '東京', 'links': {'livepocket': url2},
          'tickets': [{'type': '先着販売受付（配信）（東京 10/3〜10/4）〜10/10 20:00', 'date': '2026-10-10', 'url': url2}]}
    run1('配信・複数日の正しい登録は鳴らない', e2, p=parse_page(page2), want=False)
    m = copy.deepcopy(e2); m['dateLabel'] = '2026年10月4日(日)'
    run1('会期の型（初日欠落）', m, p=parse_page(page2), key='①')
    # 🆕2026-09-30 見出しの後ろの「（配信は…まで）」は視聴の終わり＝会期・開演時刻と食い違いにしない
    m = copy.deepcopy(e2); m['dateLabel'] = '2026年10月3日(土)〜2026年10月4日(日)（配信は10月18日(日) 23:59まで）'
    run1('配信の見出し（会期の型）は鳴らない', m, p=parse_page(page2), want=False)
    m = copy.deepcopy(good); m['dateLabel'] = '2026年10月25日(日) 19:00開演（配信は11月1日(日) 23:59まで）'
    run1('配信の見出し（開演の型）は鳴らない', m, want=False)
    m = copy.deepcopy(good); m['dateLabel'] = '2026年10月25日(日) 18:00開演（配信は11月1日(日) 23:59まで）'
    run1('配信の見出しでも開演時刻違いは鳴らす', m, key='①開演時刻')
    # 🆕2026-09-30 スタリオン型＝公演日は過去・配信の受付は締切が未来＝「終わっている」と言わない
    pageS = _mk_page(dt.date(2026, 9, 28), dt.date(2026, 9, 28), '開演時間', '22:00', '渋谷ホール', '東京都',
                     [('販売中', '配信チケット受付', D(2026, 9, 20, 10, 0), D(2026, 10, 5, 23, 59), '視聴チケット'),
                      ('販売中', '会場チケット受付', D(2026, 9, 20, 10, 0), D(2026, 9, 28, 18, 0), '一般')])
    eS = {'name': 'x', 'artist': 'x', 'date': '2026-09-28', 'dateLabel': '2026年9月28日(月) 22:00開演',
          'venue': '渋谷ホール', 'prefecture': '東京', 'links': {'livepocket': url},
          'tickets': [{'type': '配信チケット受付（東京 9/28 22:00公演）〜10/5 23:59', 'date': '2026-10-05', 'url': url}]}
    run1('公演後も買える配信だけの正しい登録は鳴らない', eS, p=parse_page(pageS), td=dt.date(2026, 9, 30), want=False)
    pageS2 = pageS.replace('2026年10月5日(月) 23:59', '2026年9月29日(火) 23:59')
    run1('締切が過ぎた配信なら⑤を鳴らす', eS, p=parse_page(pageS2), td=dt.date(2026, 9, 30), key='⑤')
    # 副札（ファンクラブチケット）は状態として読む・知らない副札は判定不能
    fc = page.replace('<span class="tag">販売中</span>', '<span class="tag">販売中</span><span class="tag">ファンクラブチケット</span>', 1)
    run1('副札ファンクラブチケットは鳴らない', good, p=parse_page(fc), want=False)
    fx = page.replace('<span class="tag">販売中</span>', '<span class="tag">販売中</span><span class="tag">謎の札</span>', 1)
    run1('知らない副札は判定不能', good, p=parse_page(fx), key='判定不能')
    # 枠の開演時刻「09:20」と「9:20」は同じ
    p9 = _mk_page(dt.date(2026, 10, 24), dt.date(2026, 10, 24), '開演時間', '09:20', '会議室', '東京都',
                  [('販売中', '先着販売受付', D(2026, 9, 20, 10, 0), D(2026, 10, 24, 9, 20), '一般')])
    e9 = {'name': 'x', 'date': '2026-10-24', 'dateLabel': '2026年10月24日(土) 09:20開演', 'venue': '会議室',
          'prefecture': '東京', 'links': {'livepocket': url},
          'tickets': [{'type': '先着販売受付（東京 10/24 09:20公演）〜10/24 9:20', 'date': '2026-10-24', 'url': url}]}
    run1('開演09:20は9:20と同じ', e9, p=parse_page(p9), want=False)
    # 日付別ページを畳んだエントリ：1ページ落ちを鳴らす
    pages3 = {}
    ents3 = []
    for k, dd in enumerate((1, 2, 3)):
        u = 'https://livepocket.jp/e/day%d' % dd
        d0 = D(2026, 11, dd, 10, 0)
        pages3[u] = parse_page(_mk_page(dt.date(2026, 11, 1), dt.date(2026, 11, 3), None, None, 'カフェ', '東京都',
                                        [('販売中', '【11/%d（%s）】来店予約' % (dd, '日月火'[k]), D(2026, 9, 20, 10, 0), d0, '一般')]))
        ents3.append({'type': '【11/%d（%s）】来店予約（東京 11/1〜11/3）〜11/%d 10:00' % (dd, '日月火'[k], dd),
                      'date': '2026-11-%02d' % dd, 'url': u})
    e3 = {'name': 'x', 'date': '2026-11-03', 'dateLabel': '2026年11月1日(日)〜11月3日(火)', 'venue': 'カフェ',
          'prefecture': '東京', 'links': {'livepocket': ents3[0]['url']}, 'tickets': ents3}
    iss, und, _, _ = check_entry(e3, pages3, today)
    ok = not (iss or und)
    print('  %s 畳んだ3日分そろい → %s' % ('OK ' if ok else 'NG ', '; '.join(x[0] for x in iss + und) or '一致'))
    fails += 0 if ok else 1
    m3 = copy.deepcopy(e3); m3['tickets'] = [ents3[0], ents3[2]]
    iss, und, _, _ = check_entry(m3, {u: pages3[u] for u in (ents3[0]['url'], ents3[2]['url'])}, today)
    ok = any('ページの無い日' in x[0] for x in iss)
    print('  %s 畳んだエントリから1ページ落ち → %s' % ('OK ' if ok else 'NG ', '; '.join(x[0] for x in iss + und) or '一致'))
    fails += 0 if ok else 1
    print('selftest: %s（NG %d）' % ('全部OK' if not fails else 'NGあり', fails))
    return 0 if not fails else 1


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    ap = argparse.ArgumentParser(description='livePocket 独立ゲート')
    ap.add_argument('--built', help='投入前の built JSON（{"entries":[...]}）')
    ap.add_argument('--ids', help='index.html の id（またはlivePocketのイベントID）をカンマ区切り')
    ap.add_argument('--limit', type=int, default=0, help='先頭N件だけ')
    ap.add_argument('--today', help='YYYY-MM-DD（既定＝今日）')
    ap.add_argument('--sleep', type=float, default=2.0, help='取得の間隔（秒・1未満は1）')
    ap.add_argument('--report', default=DEFAULT_REPORT)
    ap.add_argument('--html-dir', help='取得したHTMLを保存／保存済みがあれば使う置き場')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    today = dt.date.fromisoformat(a.today) if a.today else dt.date.today()
    sleep = max(1.0, a.sleep)
    if a.built:
        with open(a.built, encoding='utf-8') as f:
            d = json.load(f)
        entries = d['entries'] if isinstance(d, dict) else d
    else:
        entries = [e for e in load_index_events() if is_lp(e)]
        if a.ids:
            want = set(x.strip() for x in re.split(r'[,\s]+', a.ids) if x.strip())
            entries = [e for e in entries if str(e.get('id')) in want or
                       event_id_of(e['links']['livepocket']) in want]
            if not entries:
                print('指定の id が見つからない')
                return 1
    entries = [e for e in entries if is_lp(e)]
    if a.limit:
        entries = entries[:a.limit]
    return run(entries, today, sleep, a.report, a.html_dir)


if __name__ == '__main__':
    sys.exit(main())
