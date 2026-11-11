# -*- coding: utf-8 -*-
"""チケットペイ（https://www.ticketpay.jp/）の公演を取る（2026-11-12 新設・すちこ「チケットペイから作って」）。

  python tools/ticketpay_harvest.py --out tmp/ticketpay_MMDD.json              … 全カテゴリの一覧＋公演ページを全部
  python tools/ticketpay_harvest.py --limit 100 --out tmp/ticketpay_MMDD.json  … 新しい番号から100件だけ
  python tools/ticketpay_harvest.py --ids 65163,65215 --out tmp/x.json         … 番号指定（カテゴリは一覧から引く）
  python tools/ticketpay_harvest.py --selftest

## 規約・robots（2026-11-12 に読んだ）
- robots.txt＝`/secret_key/ /vhost/ /manager/ /lib/ /webapp/` だけ禁止＝一覧・公演ページはOK
- 利用規約（paymentfor.com/etc/ticketpay_user_agreement・改訂 2026-10-28）の禁止事項は**会員の申込み**の話
  （第11条⑬「自動入力等を行うソフトウェアを使用して大量に申込み…」・⑪「円滑な運営を妨げる行為」）。
  公開ページを読むこと・公演情報を案内することを禁じる条文は無い。
  ＝**申込みの画面（/booking/booking.php・ajaxSave*）には触らない／1ページごとに数秒あける**。
- 2026-11-10 の告知「海外からのアクセス制限」＝国内から読む前提。

## ページの形（2026-11-12 実測）
一覧  : 画面の JS が `GET /ajaxViewEventList.php?keyword=&category_id=<Music…>` を呼ぶ。
        🚨**セッション（PHPSESSID）が無いと空**が返る＝先に `/search/?category_id=Music` を開いてクッキーをもらう。
        カテゴリ8つ＝Music 音楽・フェス／Drama 舞台・演劇／Sports スポーツ・格闘技／Talk トーク・セミナー／
        Screening 上映会／Animation アニメ・特撮／Leisure レジャー／Event イベント（公開中を全部返す・ページ送りなし）
        1件＝`<li id="portal_event_<id>">`・状態は title_info の after_release「販売中(…まで)」／before_release「受付前(…から)」／
        sold_out「完売」「受付終了」
個別  : `https://www.ticketpay.jp/booking/?event_id=<id>`（⚠️www. 無しはトップに飛ぶ）
        状態＝`<label class="event_mark_N">受付期間中|受付前|完売|受付終了</label>`
        欄＝`<p class="event_c"><label class="label_l en">会場|会場住所|開催日|開始|開場|出演者</label><span> : …`
        販売＝`<div id="sales_period">` の 販売期間「YYYY/MM/DD (曜) HH:MM ～ YYYY/MM/DD (曜) HH:MM」・価格・席種ごとの「指定席 : 受付中」
        券種＝`<div id="ticket_type_select_<id>">` の `<h2>券種名 8,000円</h2>`
        🚨カテゴリは個別ページに無い＝一覧から引く。

## 守ること
- User-Agent に個人の情報（メール等）を入れない
- 1ページごとに既定3秒あける（--sleep）
- 読めなかった欄は空のまま残す（推測で埋めない）＝組み立て側が報告に出す
"""
import argparse
import html as H
import http.cookiejar
import io
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

BASE = 'https://www.ticketpay.jp'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
CATS = ('Music', 'Drama', 'Sports', 'Talk', 'Screening', 'Animation', 'Leisure', 'Event')
PREFS = ('北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県', '茨城県', '栃木県', '群馬県',
         '埼玉県', '千葉県', '東京都', '神奈川県', '新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県',
         '岐阜県', '静岡県', '愛知県', '三重県', '滋賀県', '京都府', '大阪府', '兵庫県', '奈良県', '和歌山県',
         '鳥取県', '島根県', '岡山県', '広島県', '山口県', '徳島県', '香川県', '愛媛県', '高知県', '福岡県',
         '佐賀県', '長崎県', '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県')

_OPENER = None


def opener():
    """セッション付きの取り手（一覧の ajax はクッキーが無いと空を返す）。"""
    global _OPENER
    if _OPENER is None:
        cj = http.cookiejar.CookieJar()
        _OPENER = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        _OPENER.addheaders = [('User-Agent', UA), ('Accept-Language', 'ja')]
    return _OPENER


def fetch(url, headers=None, tries=3):
    last = None
    for i in range(tries):
        try:
            r = opener().open(urllib.request.Request(url, headers=headers or {}), timeout=60)
            return r.read().decode('utf-8', 'replace'), r.geturl()
        except urllib.error.HTTPError as ex:
            if ex.code in (404, 403, 410):
                raise
            last = ex
        except Exception as ex:
            last = ex
        time.sleep(5 * (i + 1))
    raise last


def text(s):
    s = re.sub(r'<br\s*/?>', ' ', s or '')
    s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'\s+', ' ', H.unescape(s)).strip()


def pref_of(addr):
    """会場住所の頭（〒の後ろ）の都道府県＝OSHINAVIの書き方（「東京」「大阪」「北海道」）。
    無ければ ''（会場名の市名から当てるのは推測なのでしない）。"""
    a = re.sub(r'^〒?\s*\d{3}-?\d{4}\s*', '', (addr or '').strip())
    for p in PREFS:
        if a.startswith(p):
            return p if p == '北海道' else p[:-1]
    return ''


DT_RE = re.compile(r'(\d{4})/(\d{1,2})/(\d{1,2})\s*(?:[（(][^)）]*[)）])?\s*(\d{1,2}):(\d{2})?')
D_RE = re.compile(r'(\d{4})/(\d{1,2})/(\d{1,2})')


def iso(y, m, d):
    return '%04d-%02d-%02d' % (int(y), int(m), int(d))


def parse_period(s):
    """「2026/10/17 (土) 12:00 ～ 2026/12/11 (金) 23:59」→ [[開始iso, 'H:MM'], [終了iso, 'H:MM']]（片方だけもある）"""
    out = []
    for m in re.finditer(r'(\d{4})/(\d{1,2})/(\d{1,2})\s*(?:[（(][^)）]*[)）])?\s*(?:(\d{1,2}):(\d{2}))?', s or ''):
        hm = '%d:%s' % (int(m.group(4)), m.group(5)) if m.group(4) else ''
        out.append([iso(m.group(1), m.group(2), m.group(3)), hm])
    if not out:
        return None
    parts = re.split(r'～|〜|~', s or '', 1)
    if len(parts) == 2 and not D_RE.search(parts[0]):
        return {'start': None, 'end': out[0]}
    if len(parts) == 2 and not D_RE.search(parts[1]):
        return {'start': out[0], 'end': None}
    return {'start': out[0], 'end': out[1] if len(out) > 1 else None}


def parse_list(t):
    """カテゴリ一覧の ajax の HTML → [{id, name, list_status}]"""
    out = []
    for chunk in re.split(r'<li id="portal_event_', t)[1:]:
        m = re.match(r'(\d+)', chunk)
        if not m:
            continue
        nm = re.search(r'<h3[^>]*>(.*?)</h3>', chunk, re.S)
        ti = re.search(r'<div class="title_info">(.*?)</div><!-- \.title_info -->', chunk, re.S)
        cls = re.search(r'<div class="([a-z_]+)">', ti.group(1)) if ti else None
        out.append({'id': int(m.group(1)), 'name': text(nm.group(1)) if nm else '',
                    'list_class': cls.group(1) if cls else '',
                    'list_status': text(ti.group(1)) if ti else ''})
    return out


def harvest_lists(sleep):
    """カテゴリ8つの一覧 → {id: {'cats': [...], 'name':, 'list_status':}}"""
    fetch(BASE + '/search/?category_id=Music')        # 🚨クッキーをもらう（無いと一覧が空）
    time.sleep(sleep)
    got = {}
    counts = {}
    for c in CATS:
        u = BASE + '/ajaxViewEventList.php?' + urllib.parse.urlencode({'keyword': '', 'category_id': c})
        t, _ = fetch(u, {'X-Requested-With': 'XMLHttpRequest', 'Referer': BASE + '/search/?category_id=' + c})
        items = parse_list(t)
        cnt = re.search(r'event_search_count = (\d+)', t)
        counts[c] = (len(items), int(cnt.group(1)) if cnt else None)
        for it in items:
            g = got.setdefault(it['id'], {'cats': [], 'name': it['name'], 'list_class': it['list_class'],
                                          'list_status': it['list_status']})
            if c not in g['cats']:
                g['cats'].append(c)
        time.sleep(sleep)
    return got, counts


def _block(t, start_pat, end_pat):
    a = re.search(start_pat, t)
    if not a:
        return ''
    b = re.search(end_pat, t[a.end():])
    return t[a.start(): a.end() + (b.start() if b else 20000)]


def parse_event(t, eid):
    """公演ページ → dict。読めない欄は None/空のまま（推測しない）。"""
    if 'class="event_name"' not in t:
        raise ValueError('公演ページの形ではない（非公開・削除・トップへ飛んだ）')
    ev = {'id': int(eid), 'url': '%s/booking/?event_id=%s' % (BASE, eid)}
    m = re.search(r'<span class="event_name">(.*?)</span>', t, re.S)
    ev['name'] = text(m.group(1)) if m else ''
    m = re.search(r'<label class="event_mark_\d+"[^>]*>(.*?)</label>', t, re.S)
    ev['mark'] = text(m.group(1)) if m else ''
    fields = {}
    for m in re.finditer(r'<p class="event_c">\s*<label class="label_l en">(.*?)</label>\s*<span>(.*?)</span>', t, re.S):
        k = text(m.group(1))
        v = re.sub(r'^\s*[:：]\s*', '', text(m.group(2)))
        fields.setdefault(k, v)
    ev['fields'] = fields
    # 会場の欄には「会場座席図を確認する」のボタンが同じ span に入る型がある（65331 新木場1stRING）＝落とす
    ev['venue'] = re.sub(r'\s*会場座席図を確認する\s*', ' ', fields.get('会場') or '').strip()
    ev['address'] = fields.get('会場住所') or ''
    ev['prefecture'] = pref_of(ev['address'])
    # 「開催日」1日／「開催期間」初日〜最終日（配信・物販・展示）。期間は両端だけ書いてある＝[初日, 最終日]
    days = [iso(*x) for x in D_RE.findall(fields.get('開催日') or fields.get('開催期間') or '')]
    ev['dates'] = sorted(set(days))
    ev['date_is_range'] = bool(fields.get('開催期間'))
    st = re.findall(r'(\d{1,2}):(\d{2})', fields.get('開始') or fields.get('開始・終了時間') or '')
    ev['start_time'] = '%d:%s' % (int(st[0][0]), st[0][1]) if st else ''
    op = re.findall(r'(\d{1,2}):(\d{2})', fields.get('開場') or '')
    ev['open_time'] = '%d:%s' % (int(op[0][0]), op[0][1]) if op else ''
    perf = fields.get('出演者') or ''
    ev['performers_raw'] = perf
    # 販売情報
    sp = _block(t, r'<div id="sales_period">', r'</div><!-- #sales_period -->')
    ev['period'] = None
    ev['price'] = None
    seats = []
    for m in re.finditer(r'<label class="label_m[^"]*">(.*?)</label>\s*<span[^>]*>(.*?)</span>', sp, re.S):
        k, v = text(m.group(1)), re.sub(r'^\s*[:：]\s*', '', text(m.group(2)))
        if k == '販売期間':
            ev['period'] = parse_period(v)
            ev['period_text'] = v
        elif k == '価格':
            ev['price'] = v
        else:
            # 席種の行＝「SS席 : 8,800円 ※完売」「指定席 : 受付中」「X席 : 受付前」
            pm = re.search(r'([\d,]+)\s*円', v)
            seats.append({'name': k, 'status': v, 'price': int(pm.group(1).replace(',', '')) if pm else None,
                          'soldout': bool(re.search(r'完売|売切|売り切れ|予定枚数終了', v))})
    ev['seats'] = seats
    # 「抽選販売となります」＝販売情報の下の注意書き（class="seat_warring_msg"）。説明文（主催者の自由文）は見ない
    nodesc = re.sub(r'<div id="event_txt_cont">.*?</div>', ' ', t, flags=re.S)
    m = re.search(r'class="seat_warring_msg"[^>]*>(.*?)</', nodesc, re.S)
    ev['sale_note'] = text(m.group(1)) if m else ''
    ev['lottery'] = bool(re.search(r'抽選販売となります|抽選販売です', text(nodesc)))
    # 同じ公演の別の日時（「公演日時をお選びください」の選び）＝それぞれ別の event_id の別ページ
    sel = re.search(r'<select[^>]*id="select_event_day".*?</select>', t, re.S)
    ev['sibling_ids'] = [int(x) for x in re.findall(r'<option value="(\d+)"', sel.group(0))] if sel else []
    # 券種
    types = []
    tb = _block(t, r'<div id="ticket_type_select_%s">' % eid, r'<div class="reservation">|<!-- \.reservation_line -->')
    for m in re.finditer(r'<h2>(.*?)</h2>(.*?)(?=<h2>|$)', tb, re.S):
        raw = text(m.group(1))
        after = text(re.sub(r'<select.*?</select>', ' ', m.group(2), flags=re.S))
        pm = None
        for pm in re.finditer(r'([\d,]+)\s*円', raw):
            pass                                   # 最後の「N円」が値段（後ろに「完売」が付く型がある）
        types.append({'raw': raw, 'name': raw[:pm.start()].strip() if pm else raw,
                      'price': int(pm.group(1).replace(',', '')) if pm else None,
                      'after': after[:80],
                      # 完売の印＝h2 の直後の class="info_sold_out_mini"（説明の「完売次第終了」を拾わない）
                      'soldout': bool(re.search(r'class="info_sold_out', m.group(2))
                                      or re.search(r'完売|売切|売り切れ|予定枚数終了', raw))})
    ev['types'] = types
    # 一番下の状態札（受付終了／完売／M/D 販売開始）
    m = re.search(r'<[a-z]+ class="event_status_label"[^>]*>(.*?)</(?:div|p|span|label)>', t, re.S)
    ev['status_label'] = text(m.group(1)) if m else ''
    m = re.search(r'([\d/]+\s*\([^)]*\)\s*\d{1,2}:\d{2})\s*～\s*販売開始', text(t))
    ev['sale_start_text'] = m.group(1) if m else ''
    # 主催（お問合せ先の名称）
    m = re.search(r'<label class="label_s en">名称</label>\s*[:：]\s*(.*?)</p>', t, re.S)
    ev['organizer'] = text(m.group(1)) if m else ''
    # 説明文（出す側の申込・セミナー判定と配信の視聴期限の読み取りに使う。長いので2000字まで）
    m = re.search(r'<div id="event_txt_cont">(.*?)</div>', t, re.S)
    ev['desc'] = text(m.group(1))[:2000] if m else ''
    return ev


def _selftest():
    page = ('<span class="event_name">テスト公演 &amp; 夜</span><label class="event_mark_1" style="">受付期間中</label>'
            '<p class="event_c">\n<label class="label_l en">会場</label>\n<span>\n : 目黒 BLUES ALLEY JAPAN </span><br></p>'
            '<p class="event_c"><label class="label_l en">会場住所</label><span> : 〒153-0063 東京都目黒区目黒1-3-14</span></p>'
            '<p class="event_c"><label class="label_l en">開催日</label><span> :\n 2027/01/23 (土)\n</span></p>'
            '<p class="event_c"><label class="label_l en">開始</label><span> : 19:00 ～ </span></p>'
            '<p class="event_c"><label class="label_l en">開場</label><span>: 18:00</span></p>'
            '<p class="event_c"><label class="label_l en">出演者</label><span>: 藤崎紗矢香</span></p>'
            '<div class="ticket_info"><div id="sales_period"><p class="sales_txt"><label class="label_m en">販売期間</label>'
            '<span style="x">: 2026/10/27 (火) 14:00 <br class="br_sp">～ 2026/11/30 (月) 23:59 </span></p>'
            '<p class="sales_txt"><label class="label_m">指定席</label><span>: 完売 </span></p>'
            '</div><!-- #sales_period --> 抽選販売となります。<div id="event_txt_cont">説明</div>'
            '<div id="ticket_type_select_1"><h2> テーブル席(指定) 8,000円 </h2><select><option>1</option></select>'
            '<h2> DinnerSet 16,500円</h2><label class="info_sold_out_mini">完売</label><select></select>'
            '<h2> 一般 3,000円</h2><select></select><p class="input_ex font-90">完売次第終了</p>'
            '</div><div class="reservation"></div>'
            '<label class="label_s en">名称</label> : BLUES ALLEY JAPAN</p>')
    ev = parse_event(page, 1)
    assert ev['name'] == 'テスト公演 & 夜', ev['name']
    assert ev['mark'] == '受付期間中'
    assert ev['venue'] == '目黒 BLUES ALLEY JAPAN', ev['venue']
    assert ev['prefecture'] == '東京', ev['prefecture']
    assert ev['dates'] == ['2027-01-23'], ev['dates']                   # 年は売り場の4桁をそのまま
    assert ev['start_time'] == '19:00' and ev['open_time'] == '18:00'
    assert ev['period'] == {'start': ['2026-10-27', '14:00'], 'end': ['2026-11-30', '23:59']}, ev['period']
    assert ev['seats'] == [{'name': '指定席', 'status': '完売', 'price': None, 'soldout': True}], ev['seats']
    # 席種の行が「値段 ※完売」の型（65340）・開催期間（配信・物販 65450）・日時の選び（65443）
    p2 = page.replace('<span>: 完売 </span>', '<span>: 8,800円 <span class="soldout">※完売</span></span>') \
             .replace('開催日</label><span> :\n 2027/01/23 (土)', '開催期間</label><span> : 2026/11/18 (水) ～ 2026/12/09 (水)') \
        + '<select name="" id="select_event_day"><option value="65436">a</option><option value="65443" selected>b</option></select>'
    e2 = parse_event(p2, 1)
    assert e2['seats'][0]['price'] == 8800 and e2['seats'][0]['soldout'], e2['seats']
    assert e2['dates'] == ['2026-11-18', '2026-12-09'] and e2['date_is_range'], e2['dates']
    assert e2['sibling_ids'] == [65436, 65443], e2['sibling_ids']
    assert ev['lottery'] is True
    assert [(x['name'], x['price'], x['soldout']) for x in ev['types']] == \
        [('テーブル席(指定)', 8000, False), ('DinnerSet', 16500, True), ('一般', 3000, False)], ev['types']
    assert ev['organizer'] == 'BLUES ALLEY JAPAN'
    assert pref_of('神奈川県横浜市') == '神奈川' and pref_of('〒060-0001 北海道札幌市') == '北海道' and pref_of('横浜市中区') == '' and pref_of('') == ''
    assert parse_period('～ 2026/11/30 (月) 23:59') == {'start': None, 'end': ['2026-11-30', '23:59']}
    try:
        parse_event('<html>トップ</html>', 2)
        raise AssertionError('トップに飛んだページを公演と読まない')
    except ValueError:
        pass
    lst = ('<li id="portal_event_65163" class="search_list"><h3 style="c">JAYWALK</h3><div class="title_info">'
           '<div class="after_release">販売中(2026/11/30 (月) 23:59まで) </div></div><!-- .title_info -->'
           '<li id="portal_event_65436" class="search_list"><h3>X</h3><div class="title_info">'
           '<div class="sold_out">受付終了</div></div><!-- .title_info -->')
    li = parse_list(lst)
    assert [(x['id'], x['list_class']) for x in li] == [(65163, 'after_release'), (65436, 'sold_out')], li
    print('selftest OK（欄・県・年・販売期間・席種の完売・券種の完売・抽選・一覧）')
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=False, default='tmp/ticketpay.json')
    ap.add_argument('--limit', type=int, default=0, help='新しい番号から N 件だけ公演ページを読む（0＝全部）')
    ap.add_argument('--ids', default='', help='番号指定（カテゴリは一覧から引く）')
    ap.add_argument('--sleep', type=float, default=3.0, help='1ページごとの間（秒）＝叩きすぎない')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        sys.exit(_selftest())

    lists, counts = harvest_lists(a.sleep)
    if a.ids:
        ids = [int(x) for x in re.findall(r'\d+', a.ids)]
    else:
        ids = sorted(lists, reverse=True)              # 新着順＝番号の大きい順
        if a.limit:
            ids = ids[:a.limit]
    events, errors = [], []
    for i, eid in enumerate(ids):
        try:
            t, final = fetch('%s/booking/?event_id=%d' % (BASE, eid))
            if 'event_id=%d' % eid not in final:
                raise ValueError('トップへ飛んだ（非公開・削除）')
            ev = parse_event(t, eid)
            li = lists.get(eid) or {}
            ev['cats'] = li.get('cats') or []
            ev['list_status'] = li.get('list_status') or ''
            ev['list_class'] = li.get('list_class') or ''
            events.append(ev)
        except Exception as ex:
            errors.append({'id': eid, 'why': str(ex)[:120]})
        time.sleep(a.sleep)
    json.dump({'harvested_at': time.strftime('%Y-%m-%d %H:%M'), 'list_counts': counts,
               'listed_total': len(lists), 'events': events, 'errors': errors},
              io.open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    sys.stderr.write('ticketpay_harvest: listed=%d read=%d errors=%d -> %s\n'
                     % (len(lists), len(events), len(errors), a.out))


if __name__ == '__main__':
    main()
