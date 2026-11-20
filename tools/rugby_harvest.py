# -*- coding: utf-8 -*-
"""TicketRugby（https://ticketrugby.jp/・リーグワン／日本代表／大学ほか）の試合を取る（2026-11-20 新設）。

  python tools/rugby_harvest.py --out tmp/x1120/newv/rugby/harvest.json
  python tools/rugby_harvest.py --ids 2637790,2643235 --out tmp/x.json
  python tools/rugby_harvest.py --selftest

## 規約・robots（2026-11-20 に読んだ）
- robots.txt＝`User-agent: * / Disallow:`（空＝全部許可）
- 規約はぴあと同じく購入用の自動化の禁止だけ（依頼者が確認済み）＝**買う画面（/sales/perform/…＝ログインが要る）には触らない**。
- 🚨Cookie（セッション）を持たないと 302 が繰り返されることがある＝クッキー付きの取り手で読む。

## ページの形（2026-11-20 実測・Laravel の素の HTML）
一覧 : `GET /search?lottery=on&page=N`（5件ずつ・「抽選販売を含む」を入れる＝入れないと抽選の試合が落ちる）
       1件＝`<div class="gamelist"><a href="https://ticketrugby.jp/sales/perform/<id>">`
       状態＝`<span class="geme_status …">発売中|…</span>`・日付＝`year`＋`date`・開場／開始＝`hour_opn`／`hour_start`
       会場＝`game_place` の `<p>会場名（県）</p>`・カテゴリ＝`game_cat`・名前＝`game_name`・チーム＝`team_name`
個別 : `GET /ticket_release_info/<id>`（**ログイン不要**の「チケット発売情報」＝カードの飛び先にする）
       席種＝`<div class="game_seat_blk">` の見出し（席種名・値段・空席の印）
       その下に受付ごとに `<div class="game_seat_status …"><img src="/img/event/ico_stN(_d).png"><p>受付名 値段</p>`
       ＋`<th>販売期間</th><td>YYYY/MM/DD(曜) HH:MM～YYYY/MM/DD(曜) HH:MM</td>`
       印＝ico_st1 空席あり／ico_st2 残りわずか／ico_st3 空席なし／ico_st4 発売期間外（_d は押せない印の色違い）

## 守ること
- User-Agent に個人の情報を入れない／1ページごとに既定3秒あける（--sleep）
- 読めなかった欄は空のまま残す（推測で埋めない）
- 人間かどうかの確認画面が出たら止める（突破しない）
"""
import argparse
import datetime
import html as H
import http.cookiejar
import io
import json
import re
import sys
import time
import urllib.error
import urllib.request

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

BASE = 'https://ticketrugby.jp'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
JST = datetime.timezone(datetime.timedelta(hours=9))
ICON = {'1': '空席あり', '2': '残りわずか', '3': '空席なし', '4': '発売期間外'}


class Site:
    def __init__(self, sleep=3.0):
        self.sleep = sleep
        self.last = 0.0
        cj = http.cookiejar.CookieJar()
        self.op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        self.op.addheaders = [('User-Agent', UA), ('Accept-Language', 'ja'),
                              ('Accept', 'text/html,application/xhtml+xml,*/*;q=0.8')]
        self.calls = 0

    def get(self, url, tries=3):
        last = None
        for i in range(tries):
            w = self.sleep - (time.time() - self.last)
            if w > 0:
                time.sleep(w)
            self.last = time.time()
            self.calls += 1
            try:
                r = self.op.open(url, timeout=60)
                t = r.read().decode('utf-8', 'replace')
                if re.search(r'captcha|cf-challenge|challenge-platform', t, re.I):
                    raise RuntimeError('人間かどうかの確認画面が出た＝止める')
                return t
            except urllib.error.HTTPError as ex:
                if ex.code in (403, 404, 410):
                    raise
                last = ex
            except RuntimeError:
                raise
            except Exception as ex:
                last = ex
            time.sleep(5 * (i + 1))
        raise last

    def list_page(self, page):
        return self.get('%s/search?lottery=on&page=%d' % (BASE, page))

    def release(self, gid):
        return self.get('%s/ticket_release_info/%s' % (BASE, gid))


def text(s):
    s = re.sub(r'<br\s*/?>', ' ', s or '')
    s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'\s+', ' ', H.unescape(s).replace('　', ' ')).strip()


def pref_of(place):
    """「トヨタスポーツセンター 陸上競技場（愛知県）」→（会場名, '愛知'）。括弧が無ければ（全体, ''）。"""
    m = re.match(r'^(.*?)[（(]([^（）()]+?(?:都|道|府|県))[）)]\s*$', place or '')
    if not m:
        return (place or '').strip(), ''
    p = m.group(2)
    return m.group(1).strip(), (p if p == '北海道' else p[:-1])


def parse_list(t):
    """一覧のページ → ([{id, status, date, open, start, place, venue, prefecture, cat, name, teams}], 全件数)"""
    out = []
    for chunk in re.split(r'<div class="gamelist">', t)[1:]:
        m = re.search(r'/sales/perform/(\d+)', chunk)
        if not m:
            # 抽選の受付（/lottery/detail/<番号>）＝ページはログインが要る＝期間が読めない＝枠にしない（数だけ残す）
            lm = re.search(r'/lottery/detail/(\d+)', chunk)
            n = re.search(r'<p class="game_name">(.*?)</p>', chunk, re.S)
            out.append({'lottery_id': int(lm.group(1)) if lm else None, 'name': text(n.group(1)) if n else '',
                        'status': text((re.search(r'<span class="geme_status[^"]*">(.*?)</span>', chunk, re.S) or [None, ''])[1])})
            continue
        g = {'id': int(m.group(1))}
        s = re.search(r'<span class="geme_status[^"]*">(.*?)</span>', chunk, re.S)
        g['status'] = text(s.group(1)) if s else ''
        y = re.search(r'<span class="year[^"]*">\s*(\d{4})\.?\s*</span>', chunk)
        d = re.search(r'<span class="date[^"]*">\s*(\d{1,2})\.(\d{1,2})\s*</span>', chunk)
        g['date'] = '%s-%02d-%02d' % (y.group(1), int(d.group(1)), int(d.group(2))) if y and d else ''
        o = re.search(r'hour_opn">.*?<span class="hour[^"]*">\s*(\d{1,2}:\d{2})', chunk, re.S)
        st = re.search(r'hour_start">.*?<span class="hour[^"]*">\s*(\d{1,2}:\d{2})', chunk, re.S)
        g['open'] = o.group(1) if o else ''
        g['start'] = st.group(1) if st else ''
        p = re.search(r'<div class="game_place">.*?<p>(.*?)</p>', chunk, re.S)
        g['place'] = text(p.group(1)) if p else ''
        g['venue'], g['prefecture'] = pref_of(g['place'])
        c = re.search(r'<span class="game_cat[^"]*">(.*?)</span>', chunk, re.S)
        g['cat'] = text(c.group(1)) if c else ''
        n = re.search(r'<p class="game_name">(.*?)</p>', chunk, re.S)
        g['name'] = text(n.group(1)) if n else ''
        g['teams'] = [text(x) for x in re.findall(r'<p class="team_name">(.*?)</p>', chunk, re.S)]
        out.append(g)
    # 「1～5件 / 66件」＝pager_num_en の2つ目（数だけの方）が全件数
    tot = re.findall(r'pager_num_en">\s*([\d,]+)\s*</span>', t)
    total = int(tot[0].replace(',', '')) if tot else None
    return out, total


PERIOD_RE = re.compile(r'(\d{4})/(\d{1,2})/(\d{1,2})\([^)]*\)\s*(\d{1,2}):(\d{2})\s*[～〜~]\s*'
                       r'(?:(\d{4})/(\d{1,2})/(\d{1,2})\([^)]*\)\s*(\d{1,2}):(\d{2}))?')


def parse_period(s):
    m = PERIOD_RE.search(s or '')
    if not m:
        return None, None
    a = '%s-%02d-%02d %d:%s' % (m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4)), m.group(5))
    b = None
    if m.group(6):
        b = '%s-%02d-%02d %d:%s' % (m.group(6), int(m.group(7)), int(m.group(8)), int(m.group(9)), m.group(10))
    return a, b


def parse_release(t):
    """チケット発売情報のページ → {title, seats:[{seat, price, icon, windows:[{name, raw, icon, start, end, period_text}]}]}"""
    if 'game_seat_wrap' not in t and 'チケット発売情報' not in t:
        raise ValueError('チケット発売情報のページの形ではない')
    ev = {}
    n = re.search(r'<p class="game_name">(.*?)</p>', t, re.S)
    ev['name'] = text(n.group(1)) if n else ''
    seats = []
    for blk in re.split(r'<div class="game_seat_blk', t)[1:]:
        head = re.search(r'<div class="game_seat_status pull_btn">\s*<div class="img">\s*<img src="[^"]*ico_st(\d)[^"]*"'
                         r'.*?<p>(.*?)</p>(?:\s*<p>(.*?)</p>)?', blk, re.S)
        seat = {'seat': text(head.group(2)) if head else '', 'price': text(head.group(3)) if head and head.group(3) else '',
                'icon': ICON.get(head.group(1), '') if head else '', 'windows': []}
        for m in re.finditer(r'<div class="game_seat_status link[^"]*">\s*<div class="img">\s*<img src="[^"]*ico_st(\d)[^"]*"[^>]*>'
                             r'\s*</div>\s*<p>(.*?)</p>\s*</div>\s*<table[^>]*>(.*?)</table>', blk, re.S):
            raw = text(m.group(2))
            per = re.search(r'<th>\s*販売期間\s*</th>\s*<td>(.*?)</td>', m.group(3), re.S)
            pt = text(per.group(1)) if per else ''
            a, b = parse_period(pt)
            nm = re.sub(r'\s*[\d,]+円(?:\s*[～〜~]\s*[\d,]+円)?\s*$', '', raw).strip()
            seat['windows'].append({'name': nm, 'raw': raw, 'icon': ICON.get(m.group(1), ''),
                                    'start': a, 'end': b, 'period_text': pt})
        seats.append(seat)
    ev['seats'] = seats
    ev['lottery_words'] = bool(re.search(r'抽選', text(t)))
    return ev


def harvest(site, ids=None, log=sys.stderr):
    listed, lottery, total, page = {}, {}, None, 1
    while True:
        items, tot = parse_list(site.list_page(page))
        total = tot if tot is not None else total
        for g in items:
            if 'id' in g:
                listed.setdefault(g['id'], g)
            else:
                lottery.setdefault(g['lottery_id'], g)
        if not items or (total is not None and len(listed) + len(lottery) >= total) or page > 60:
            break
        page += 1
    want = ids or sorted(listed, key=lambda i: (listed[i]['date'], i))
    events, errors = [], []
    for gid in want:
        try:
            r = parse_release(site.release(gid))
            ev = dict(listed.get(gid) or {'id': gid})
            ev['release'] = r
            ev['url'] = '%s/ticket_release_info/%s' % (BASE, gid)
            events.append(ev)
        except RuntimeError:
            raise
        except Exception as ex:
            errors.append({'id': gid, 'why': str(ex)[:120]})
    return {'listed_total': total, 'listed_read': len(listed), 'pages': page, 'events': events, 'errors': errors,
            'lottery_login_only': list(lottery.values())}


def _selftest():
    lst = ('<div class="gamelist"><a href="\n https://ticketrugby.jp/sales/perform/2637790\n " class="gamelist_a">'
           '<span class="geme_status geme_status2">発売中</span><span class="year font_en">2026.</span>'
           '<span class="date font_en">11.21</span><span class="hour_opn"><span class="txt1">開場</span>'
           '<span class="hour font_en">11:00</span></span><span class="hour_start"><span class="txt1">開始</span>'
           '<span class="hour font_en">13:00</span></span><div class="game_place"><span class="ico"></span>'
           '<p>トヨタスポーツセンター　陸上競技場（愛知県）</p></div><span class="game_cat game_cat4">その他 </span>'
           '<p class="game_name">\n トヨタヴェルブリッツ対静岡ブルーレヴズ プレシーズンマッチ\n</p>'
           '<p class="team_name">トヨタヴェルブリッツ</p><p class="team_name">静岡ブルーレヴズ</p></a></div>'
           '<span class="font_en pager_num_en">1～5</span>件 / <span class="font_en pager_num_en">66</span>件')
    items, tot = parse_list(lst)
    assert tot == 66 and len(items) == 1, (items, tot)
    g = items[0]
    assert (g['id'], g['status'], g['date'], g['open'], g['start']) == (2637790, '発売中', '2026-11-21', '11:00', '13:00'), g
    assert (g['venue'], g['prefecture'], g['cat']) == ('トヨタスポーツセンター 陸上競技場', '愛知', 'その他'), g
    assert g['teams'] == ['トヨタヴェルブリッツ', '静岡ブルーレヴズ'] and g['name'].endswith('プレシーズンマッチ')
    rel = ('チケット発売情報<div class="game_seat_wrap"><div class="game_seat_blk pull_wrap">'
           '<div class="game_seat_status pull_btn"><div class="img"><img src="/img/event/ico_st3.png" alt=""></div>'
           '<div style="display: block"><p>指定席（ピッチサイドシート）</p><p>4,000円</p></div></div>'
           '<div class="pull_content"><div class="game_seat_status link seat_selection_popup ) link_null ">'
           '<div class="img"><img src="/img/event/ico_st4_d.png" alt=""></div><p>【トヨタV】一次先行発売 4,000円</p></div>'
           '<table class="game_pttl_tbl"><tbody><tr><th>販売期間</th><td>2026/10/10(土) 10:00～2026/10/17(土) 9:59</td></tr></tbody></table>'
           '<div class="game_seat_status link seat_selection_popup ) link_null "><div class="img"><img src="/img/event/ico_st3_d.png" alt="">'
           '</div><p>一般発売 1,000円～2,000円</p></div><table class="game_pttl_tbl"><tbody><tr><th>販売期間</th>'
           '<td>2026/10/17(土) 10:00～2026/11/21(土) 14:00</td></tr></tbody></table></div></div></div>')
    r = parse_release(rel)
    s = r['seats'][0]
    assert (s['seat'], s['price'], s['icon']) == ('指定席（ピッチサイドシート）', '4,000円', '空席なし'), s
    assert [(w['name'], w['icon'], w['start'], w['end']) for w in s['windows']] == [
        ('【トヨタV】一次先行発売', '発売期間外', '2026-10-10 10:00', '2026-10-17 9:59'),
        ('一般発売', '空席なし', '2026-10-17 10:00', '2026-11-21 14:00')], s['windows']
    assert parse_period('2026/12/01(火) 10:00～') == ('2026-12-01 10:00', None)
    assert pref_of('秩父宮ラグビー場（東京都）') == ('秩父宮ラグビー場', '東京') and pref_of('X') == ('X', '')
    assert pref_of('札幌ドーム（北海道）') == ('札幌ドーム', '北海道')
    try:
        parse_release('<html>エラー</html>')
        raise AssertionError('形の違うページを読まない')
    except ValueError:
        pass
    print('selftest OK（一覧の欄・全件数・会場と県・チーム・席種・受付名・印・販売期間・終わりの無い期間）')
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='tmp/rugby.json')
    ap.add_argument('--ids', default='')
    ap.add_argument('--sleep', type=float, default=3.0)
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        sys.exit(_selftest())
    site = Site(a.sleep)
    ids = [int(x) for x in re.findall(r'\d+', a.ids)] or None
    d = harvest(site, ids)
    d['harvested_at'] = datetime.datetime.now(JST).strftime('%Y-%m-%d %H:%M')
    json.dump(d, io.open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    sys.stderr.write('rugby_harvest: listed=%s/%s read=%d errors=%d calls=%d -> %s\n'
                     % (d['listed_read'], d['listed_total'], len(d['events']), len(d['errors']), site.calls, a.out))


if __name__ == '__main__':
    main()
