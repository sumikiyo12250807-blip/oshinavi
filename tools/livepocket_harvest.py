# -*- coding: utf-8 -*-
"""livePocket（ライブポケット・新サイト livepocket.jp）のイベントを取る。

  python tools/livepocket_harvest.py --stop-known 1 --out tmp/livepocket_MMDD.json   … 毎朝用
  python tools/livepocket_harvest.py --pages 5 --out tmp/lp.json                     … 新着の先頭5ページだけ
  python tools/livepocket_harvest.py --ids kba4t,meltiq26-11-08 --out tmp/lp.json    … 個別を指定
  python tools/livepocket_harvest.py --selftest

## なぜ livePocket か（2026-09-27 下調べ・2026-09-28 ユーザー「livePocket作って」）
開催予定 約8,000件。地下・ライブアイドルの生誕祭／定期公演、ライブハウスの対バン、ロフト系のトーク、
お笑い、ヴィジュアル系。ぴあに出てこない小さな公演が多い（下調べ＝tmp/x0927/new_vendors_survey.md）。
🚨`t.livepocket.jp` は**旧サイト**（開催予定3件だけ）。今のサイトは `livepocket.jp`。

## ページの形（2026-09-28 実測）
一覧  : https://livepocket.jp/event/search?sort=3&page=N   … sort=3＝公開日が新しい順（新着）・1ページ20件・最大500ページ
        <a class="event-card …" href="/e/{id}"> … <span class="… event-card__tag">販売中</span>
        ⚠️一覧のカードにカテゴリは無い（個別ページの「同じカテゴリーのイベントを検索」にある）
個別  : https://livepocket.jp/e/{id}   （id は英数字。主催者が付けた文字列のこともある＝重複判定はこの id で）
        h1.heading01                         … 公演名
        概要 dl（開催日／開演時間・開場時間／会場「LOFT9 Shibuya (東京都)」／出演者／販売元）
        li.event-detail-ticket__item          … **受付**ごと（先着販売受付・抽選受付 など）
          head__status の span.tag-*          … 受付の状態（販売前／販売中／販売終了／売切 …）
          span.label-order                    … 先着／抽選
          head__list-data                     … 「2026年9月28日(月) 20:00〜2026年11月25日(水) 00:00」
                                                 （販売中になると開始が消えて「〜終了」だけになる型がある）
          section.event-detail-ticket-card    … 券種（h4 名前・span.tag-* 状態・¥価格）
        tag-area「同じカテゴリーのイベントを検索」 … l_cat（大分類）＋ s_cat（小分類）
        JSON-LD                               … startDate は**時刻がいつも T00:00**（時刻には使わない）
"""
import argparse
import gzip
import html as _html
import io
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
except Exception:
    pass

BASE = 'https://livepocket.jp'
UA = {'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                     '(KHTML, like Gecko) Chrome/120.0 Safari/537.36 OSHINAVI-harvest'),
      'Accept-Language': 'ja,en;q=0.8'}
PREF47 = ('北海道 青森県 岩手県 宮城県 秋田県 山形県 福島県 茨城県 栃木県 群馬県 埼玉県 千葉県 東京都 '
          '神奈川県 新潟県 富山県 石川県 福井県 山梨県 長野県 岐阜県 静岡県 愛知県 三重県 滋賀県 京都府 '
          '大阪府 兵庫県 奈良県 和歌山県 鳥取県 島根県 岡山県 広島県 山口県 徳島県 香川県 愛媛県 高知県 '
          '福岡県 佐賀県 長崎県 熊本県 大分県 宮崎県 鹿児島県 沖縄県').split()
ID_RE = r'[A-Za-z0-9_\-]+'


def fetch(url, tries=3):
    for i in range(tries):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40)
            raw = r.read()
            if r.headers.get('Content-Encoding') == 'gzip':
                raw = gzip.decompress(raw)
            return raw.decode('utf-8', 'replace')
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise
            if i == tries - 1:
                raise
            time.sleep(3 * (i + 1))
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(3 * (i + 1))


def strip_tags(s):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s or '')).strip()


def txt(s):
    return _html.unescape(strip_tags(s))


def pref_of(text):
    """「LOFT9 Shibuya (東京都)」→「東京」。47都道府県の名前しか県として認めない。"""
    for p in PREF47:
        if p in (text or ''):
            return p if p == '北海道' else p[:-1]
    return None


def parse_jp_dt(s):
    """「2026年9月28日(月) 20:00」→ ('2026-09-28', '20:00')。時刻が無ければ ('2026-09-28', '')。"""
    m = re.search(r'(\d{4})年\s*(\d{1,2})月\s*(\d{1,2})日(?:\s*[（(][^)）]*[)）])?\s*(?:(\d{1,2}):(\d{2}))?', s or '')
    if not m:
        return None
    d = '%04d-%02d-%02d' % (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    t = '%d:%s' % (int(m.group(4)), m.group(5)) if m.group(4) else ''
    return d, t


def parse_period(s):
    """受付期間の文字 → {'start': (iso, hm)|None, 'end': (iso, hm)|None, 'text': 元の文字}
    形は3つ（2026-09-28 実測）：
      「2026年9月28日(月) 20:00〜2026年11月25日(水) 00:00」 … 開始と終了
      「〜2026年11月7日(土) 23:59」                          … 販売中になって開始が消えた形
      「2026年10月1日(木) 10:00〜」                          … 終了が書いていない形
    🚨どちらか読めない側は None のまま（推測で埋めない）。"""
    t = _html.unescape(s or '').replace('～', '〜').replace('~', '〜')
    t = re.sub(r'\s+', ' ', t).strip()
    out = {'start': None, 'end': None, 'text': t}
    if '〜' in t:
        a, b = t.split('〜', 1)
    else:
        a, b = t, ''
    out['start'] = parse_jp_dt(a)
    out['end'] = parse_jp_dt(b)
    return out


def parse_list_page(h):
    """一覧ページ → [(id, カードの状態タグ, カードの公演名)], 最大ページ番号"""
    rows = []
    # 🚨ページには「おすすめ」などほかの帯のカードも並ぶ（2026-09-28 実測＝1ページ20件のはずが28〜36件取れた）。
    #    新着の一覧（イベント一覧の節）だけを見る。
    sm = re.search(r'<!-- ### イベント一覧 start ### -->(.*?)(?:<div class="pagination"|<!-- ### イベント一覧 end ### -->)', h, re.S)
    if sm:
        h_list = sm.group(1)
    else:
        h_list = h
    for m in re.finditer(r'<a class="event-card[^"]*"[^>]*href="/e/(' + ID_RE + r')">(.*?)</a>', h_list, re.S):
        eid, blk = m.group(1), m.group(2)
        tag = re.search(r'event-card__tag">([^<]+)<', blk)
        ttl = re.search(r'event-card__title">(.*?)</h3>', blk, re.S)
        dt = re.search(r'event-card__date">日程</span>(.*?)</p>', blk, re.S)
        if eid not in [r[0] for r in rows]:
            rows.append((eid, tag.group(1).strip() if tag else '', txt(ttl.group(1)) if ttl else '',
                         txt(dt.group(1)) if dt else ''))
    pages = {int(x) for x in re.findall(r'[?&]page=(\d+)', _html.unescape(h))} | {1}
    return rows, max(pages)


def _info_block(h, label):
    """概要の dl から見出し（開催日・会場・出演者・販売元）の dd を取る（PC版の概要を使う）。"""
    m = re.search(r'<span class="event-detail-info__\w+">' + label + r'</span></dt>\s*<dd class="event-detail-info__data[^"]*">(.*?)</dd>\s*</div>',
                  h, re.S)
    return m.group(1) if m else ''


def parse_event(h, eid):
    out = {'id': eid, 'url': f'{BASE}/e/{eid}', 'name': None, 'dates': [], 'date_text': '',
           'open_time': None, 'start_time': None, 'venue': None, 'venue_raw': '', 'prefecture': None,
           'performers': [], 'organizer': None, 'cats': [], 'receptions': []}
    m = re.search(r'<h1 class="heading01">(.*?)</h1>', h, re.S)
    if m:
        out['name'] = txt(m.group(1))
    # 開催日（1日だけ／「〜」で範囲のこともある）
    dtxt = txt(_info_block(h, '開催日'))
    out['date_text'] = dtxt
    out['dates'] = ['%04d-%02d-%02d' % (int(a), int(b), int(c))
                    for a, b, c in re.findall(r'(\d{4})年\s*(\d{1,2})月\s*(\d{1,2})日', dtxt)]
    tm = _info_block(h, '時間')
    # 時間の欄は「見出し＋時刻」の組。見出しはふつう 開演時間／開場時間 だが、主催者が自由に書く形がある
    #   （2026-09-28 実例＝POP UP の「WUCA 15:00」。同じ名前・同じ日の別ページが8つあり、違いはここだけ）。
    #   大きく出ている1つ目を主の時刻とし、見出しも持つ。
    pairs = [(txt(a), b) for a, b in re.findall(r'<dt class="event-detail-info-time__title">(.*?)</dt>\s*'
                                               r'<dd class="event-detail-info-time__date">\s*(\d{1,2}:\d{2})', tm, re.S)]
    out['times'] = pairs
    om = [b for a, b in pairs if a == '開場時間']
    sm = [b for a, b in pairs if a == '開演時間']
    out['open_time'] = om[0] if om else None
    out['start_time'] = sm[0] if sm else (pairs[0][1] if pairs and pairs[0][0] != '開場時間' else None)
    out['start_label'] = '開演時間' if sm else (pairs[0][0] if out['start_time'] else None)
    # 会場の dd ＝「WUCA TOKYO (東京都)」＋ <span>住所</span> ＋ 地図リンク。
    #   🚨dd を丸ごと文字にすると住所まで会場名に入る（2026-09-28 初版で全件そうなった）＝最初の < までが会場名
    vb = _info_block(h, '会場')
    ven = _html.unescape(re.split(r'<', vb.strip(), 1)[0]).strip()
    ven = re.sub(r'\s+', ' ', ven)
    am = re.search(r'<span>(.*?)</span>', vb, re.S)
    out['venue_address'] = txt(am.group(1)) if am else ''
    out['venue_raw'] = ven
    pm = re.search(r'\s*[（(]([^()（）]*)[)）]\s*$', ven)
    # 県＝会場名の後ろのカッコ（livePocket自身が持っている都道府県）。「(その他)」は県なし。
    #   カッコで取れない時だけ住所に書かれた県名を使う（住所の文字＝事実。市名から当てる推測はしない）
    out['prefecture'] = (pref_of(pm.group(1)) if pm else None) or pref_of(out['venue_address'])
    out['venue'] = (ven[:pm.start()] if pm else ven).strip() or None
    out['performers'] = [txt(x) for x in re.findall(r'<a class="event-detail-info-list__link"[^>]*>(.*?)</a>',
                                                    _info_block(h, '出演者'), re.S)]
    org = txt(_info_block(h, '販売元'))
    out['organizer'] = org or None
    # カテゴリ（「同じカテゴリーのイベントを検索」の l_cat／s_cat）
    cm = re.search(r'同じカテゴリーのイベントを検索</p>(.*?)</ul>', h, re.S)
    if cm:
        for q in re.findall(r'href="/event/search\?([^"]+)"', cm.group(1)):
            qs = urllib.parse.parse_qs(_html.unescape(q))
            k = [qs.get('l_cat', [''])[0], qs.get('s_cat', [''])[0]]
            if k not in out['cats']:
                out['cats'].append(k)
    # 受付・チケット情報
    sec = re.search(r'<section id="ticket"(.*?)<!-- ### 受付・チケット情報 end ### -->', h, re.S)
    body = sec.group(1) if sec else ''
    parts = re.split(r'<li class="event-detail-ticket__item', body)[1:]
    for p in parts:
        head, _, rest = p.partition('</a>')
        st = re.search(r'event-detail-ticket-head__status">\s*<span class="(tag-[\w-]+)">([^<]*)</span>', head)
        tt = re.search(r'<h3 class="event-detail-ticket-head__title">(.*?)</h3>', head, re.S)
        # 先着＝span.label-order／抽選＝span.label-lottery（2026-09-28 実測。初版は抽選を読めていなかった）
        order = re.search(r'<span class="label-(?:order|lottery)">([^<]*)</span>', head)
        title = tt.group(1) if tt else ''
        title = re.sub(r'<span class="label-[\w-]+">[^<]*</span>', '', title)
        per_items = []
        for lt, ld in re.findall(r'<dt class="event-detail-ticket-head__list-title">(.*?)</dt>\s*'
                                 r'<dd class="event-detail-ticket-head__list-data">(.*?)</dd>', head, re.S):
            per_items.append({'label': txt(lt), 'text': txt(ld.replace('<br class="only-sp" />', ''))})
        rec = {'status': st.group(2).strip() if st else '', 'status_class': st.group(1) if st else '',
               'order': order.group(1).strip() if order else '', 'title': txt(title),
               'periods': per_items, 'period': None, 'cards': [],
               'button': None, 'note': ''}
        for it in per_items:
            if '期間' in it['label'] or '受付' in it['label']:
                rec['period'] = parse_period(it['text'])
                break
        if rec['period'] is None and per_items:
            rec['period'] = parse_period(per_items[0]['text'])
        nt = re.search(r'event-detail-ticket-body__sub-text">(.*?)</p>', rest, re.S)
        rec['note'] = txt(nt.group(1))[:300] if nt else ''
        for c in re.split(r'<section class="event-detail-ticket-card">', rest)[1:]:
            cn = re.search(r'<h4 class="event-detail-ticket-card__title">(.*?)</h4>', c, re.S)
            cs = re.search(r'event-detail-ticket-card__status">\s*<span class="(tag-[\w-]+)">([^<]*)</span>', c)
            cp = re.search(r'event-detail-ticket-card__price">\s*<span>\s*[¥￥]\s*([0-9,]+)', c)
            ctx = re.search(r'event-detail-ticket-card__text[^"]*"[^>]*>(.*?)</p>', c, re.S)
            rec['cards'].append({'name': txt(cn.group(1)) if cn else '',
                                 'status': cs.group(2).strip() if cs else '',
                                 'status_class': cs.group(1) if cs else '',
                                 'price': int(cp.group(1).replace(',', '')) if cp else None,
                                 'text': txt(ctx.group(1))[:200] if ctx else ''})
        bt = re.search(r'<a class="button-paramount[^"]*"[^>]*>(.*?)</a>', rest, re.S)
        rec['button'] = txt(bt.group(1)) if bt else None
        out['receptions'].append(rec)
    return out


def _selftest():
    assert parse_jp_dt('2026年9月28日(月) 20:00') == ('2026-09-28', '20:00')
    assert parse_jp_dt('2026年11月7日(土)') == ('2026-11-07', '')
    p = parse_period('2026年9月28日(月) 20:00〜2026年11月25日(水) 00:00')
    assert p['start'] == ('2026-09-28', '20:00') and p['end'] == ('2026-11-25', '0:00'), p
    p = parse_period('〜2026年11月7日(土) 23:59')
    assert p['start'] is None and p['end'] == ('2026-11-07', '23:59'), p
    p = parse_period('2026年10月1日(木) 10:00〜')
    assert p['start'] == ('2026-10-01', '10:00') and p['end'] is None, p
    assert pref_of('東京都') == '東京' and pref_of('北海道') == '北海道' and pref_of('某所') is None
    lst = ('<a class="event-card event-card" data-turbo="false" href="/e/kba4t"><span class="tag-tertiary event-card__tag">販売前</span>'
           '<h3 class="event-card__title">A</h3><p class="event-card__text event-card__text--date">'
           '<span class="event-card__date">日程</span> 2026年11月25日(水) </p></a>'
           '<a href="/event/search?sort=3&page=500" class="pagination__button">500</a>')
    rows, mx = parse_list_page(lst)
    assert rows == [('kba4t', '販売前', 'A', '2026年11月25日(水)')] and mx == 500, (rows, mx)
    # 実ページの見本（保存があれば）
    try:
        h = io.open('tmp/lp/raw/kba4t.html', encoding='utf-8').read()
    except Exception:
        h = None
    if h:
        d = parse_event(h, 'kba4t')
        assert d['name'] == '《一般販売》「虹の黄昏と空気階段」', d['name']
        assert d['dates'] == ['2026-11-25'] and d['start_time'] == '19:30' and d['open_time'] == '18:30', d
        assert d['venue'] == 'LOFT9 Shibuya' and d['prefecture'] == '東京', (d['venue'], d['prefecture'])
        assert d['performers'] == ['虹の黄昏', '空気階段'], d['performers']
        assert ['展覧会・イベント', 'トークショー'] in d['cats'], d['cats']
        r = d['receptions'][0]
        assert r['status'] == '販売前' and r['order'] == '先着' and r['title'] == '先着販売受付', r
        assert r['period']['start'] == ('2026-09-28', '20:00') and r['period']['end'] == ('2026-11-25', '0:00'), r
        assert r['cards'][0]['name'] == '会場チケット' and r['cards'][0]['price'] == 3000, r['cards']
    # 🚨会場の dd に住所が続く形（住所を会場名に入れない）
    vb = ('<span class="event-detail-info__place">会場</span></dt>\n<dd class="event-detail-info__data">\n'
          ' WUCA TOKYO (東京都)\n <span>渋谷区神南1-5-7\n </span>\n <div class="x"><a>地図</a></div>\n</dd>\n</div>')
    tb = ('<span class="event-detail-info__time">時間</span></dt>\n<dd class="event-detail-info__data x">\n'
          '<dl><dt class="event-detail-info-time__title">WUCA</dt>\n<dd class="event-detail-info-time__date">15:00</dd></dl>\n</dd>\n</div>')
    dt_ = parse_event(tb, 't')
    assert dt_['start_time'] == '15:00' and dt_['start_label'] == 'WUCA' and dt_['open_time'] is None, dt_
    dv = parse_event(vb, 'x')
    assert dv['venue'] == 'WUCA TOKYO' and dv['prefecture'] == '東京' and dv['venue_address'] == '渋谷区神南1-5-7', dv
    dv2 = parse_event(vb.replace('(東京都)', '(その他)'), 'x')
    assert dv2['prefecture'] is None and dv2['venue'] == 'WUCA TOKYO', dv2
    # 🚨抽選の札は label-lottery
    lt = ('<section id="ticket"><li class="event-detail-ticket__item js-toggle "><a href="">'
          '<div class="event-detail-ticket-head__status"><span class="tag-primary">販売中</span></div>'
          '<h3 class="event-detail-ticket-head__title"><span class="label-lottery">抽選</span> 抽選販売受付　大阪 </h3>'
          '<dl class="event-detail-ticket-head__list"><dt class="event-detail-ticket-head__list-title">販売受付期間</dt>'
          '<dd class="event-detail-ticket-head__list-data">2026年9月28日(月) 20:00<br class="only-sp" />〜2026年10月1日(木) 23:59</dd></dl></a>'
          '</li><!-- ### 受付・チケット情報 end ### -->')
    rl = parse_event(lt, 'y')['receptions'][0]
    assert rl['order'] == '抽選' and rl['title'] == '抽選販売受付 大阪', rl
    print('selftest OK: parse_jp_dt/parse_period/pref_of/parse_list_page' + ('/parse_event(実ページ)' if h else ''))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='tmp/livepocket_harvest.json')
    ap.add_argument('--sleep', type=float, default=1.0, help='1回ごとの間（秒）。礼儀として1秒前後')
    ap.add_argument('--pages', type=int, default=0, help='一覧を先頭から何ページまで見るか（0＝最後まで／打ち切りまで）')
    ap.add_argument('--start-page', type=int, default=1)
    ap.add_argument('--limit', type=int, default=0, help='個別ページを引く上限（試すとき）')
    ap.add_argument('--sort', type=int, default=3, help='一覧の並び 3＝公開日が新しい順（毎朝用）／1＝開催日が新しい順（遠い先の公演から＝発売前が多い・9/28夜）')
    ap.add_argument('--stop-known', type=int, default=0,
                    help='登録済みだけのページがこの回数続いたら一覧を打ち切る（毎朝用は 1）。個別も未登録だけ引く')
    ap.add_argument('--ids', default='', help='個別idを直接指定（一覧を回さない）')
    ap.add_argument('--index', default='index.html')
    a = ap.parse_args()

    known = set()
    if a.stop_known:
        try:
            known = set(re.findall(r'livepocket\.jp/e/(' + ID_RE + ')',
                                   io.open(a.index, encoding='utf-8', newline='').read()))
            print(f'  登録済みの livePocket イベント {len(known)}件（新着順で追い越したら打ち切る）')
        except Exception as e:
            print(f'  ⚠️登録済みidが読めなかった（打ち切りなしで回す）: {str(e)[:60]}')

    listed, order = {}, []
    if a.ids:
        order = [x.strip() for x in a.ids.split(',') if x.strip()]
    else:
        page, last, allknown = a.start_page, a.start_page, 0
        while page <= last:
            u = f'{BASE}/event/search?sort={a.sort}&page={page}'
            try:
                h = fetch(u)
            except Exception as e:
                print(f'  一覧 page={page} ERR {str(e)[:60]}')
                break
            rows, mx = parse_list_page(h)
            last = max(last, mx)
            if a.pages:
                last = min(last, a.start_page + a.pages - 1)
            for eid, tag, ttl, dtx in rows:
                if eid not in listed:
                    listed[eid] = {'tag': tag, 'title': ttl, 'date_text': dtx, 'page': page}
                    order.append(eid)
            fresh = [r[0] for r in rows if r[0] not in known]
            print(f'  一覧 page={page}/{last} … {len(rows)}件（未登録{len(fresh)}件）/ 累計{len(order)}件')
            page += 1
            time.sleep(a.sleep)
            if not rows:
                break
            if a.stop_known and known:
                allknown = allknown + 1 if not fresh else 0
                if allknown >= a.stop_known:
                    print(f'  → 登録済みだけのページが{allknown}枚続いたので打ち切り')
                    break
        a.last_page_seen = page - 1

    if a.stop_known and known:
        sk = [i for i in order if i in known]
        order = [i for i in order if i not in known]
        print(f'  登録済み {len(sk)}件は個別ページを引かない / これから引く {len(order)}件')
    todo = order[:a.limit] if a.limit else order
    rows, errs = [], []
    for n, eid in enumerate(todo, 1):
        try:
            d = parse_event(fetch(f'{BASE}/e/{eid}'), eid)
            d['list'] = listed.get(eid) or {}
            rows.append(d)
            ns = sum(len(r['cards']) for r in d['receptions'])
            print(f'  [{n}/{len(todo)}] {eid} {(d["name"] or "")[:30]} 受付{len(d["receptions"])}/券種{ns}')
        except Exception as e:
            errs.append({'id': eid, 'error': str(e)[:120]})
            print(f'  [{n}/{len(todo)}] {eid} ERR {str(e)[:60]}')
        time.sleep(a.sleep)
    json.dump({'source': 'livepocket', 'fetched_at': time.strftime('%Y-%m-%d %H:%M'),
               'last_page_seen': getattr(a, 'last_page_seen', None),
               'listed': len(listed), 'events': rows, 'errors': errs},
              io.open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    st = {}
    for r in rows:
        for rc in r['receptions']:
            st[rc['status']] = st.get(rc['status'], 0) + 1
    print(f'\n=== イベント {len(rows)}件 / 読めなかった {len(errs)}件 → {a.out} ===')
    print('受付の状態:', sorted(st.items(), key=lambda x: -x[1]))


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        _selftest()
        sys.exit(0)
    main()
