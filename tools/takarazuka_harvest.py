# -*- coding: utf-8 -*-
"""宝塚歌劇（kageki.hankyu.co.jp・販売は宝塚歌劇Webチケットサービス）の公演を集める。

  python tools/takarazuka_harvest.py --out tmp/x1120/newv/takarazuka/harvest.json
  python tools/takarazuka_harvest.py --urls /revue/2026/rrr/ticket_tokyo.html     … ページを名指し
  python tools/takarazuka_harvest.py --selftest

## 規約・robots（2026-11-20）
- 規約はすちこが確認済み（ボットの条文なし、または購入用ボットの禁止だけ）。robots.txt は無い（404）。
- フッターに「掲載情報の複製・改変を禁止」＝**紹介文・配役・注意書き・画像は写さない**（公演名・会期・劇場・受付の日時の事実だけ）。
- 販売の takarazuka-ticket.com は会員ログインの作り＝**読まない**。公式の公演案内の「チケット」ページ（誰でも見られる）だけ読む。
  1ページごとに3秒以上あける・同時に1本だけ。

## 一覧の取り方（2026-11-20 実測・静的 HTML・UTF-8）
- 入口①「チケット購入」`/ticket/index.html`＝いま売っている公演の `ticket_<劇場>.html#purchase` へのリンク。
- 入口②「公演案内」`/revue/index.html` → 公演ごとの `/revue/<年>/<名>/index.html` → その中の `ticket_<劇場>.html`
  （①に出ない先の公演＝友の会の先行だけ始まっている公演がここにある。例 2027 abunaideka）。
- 入口③ チケットページの「会場を選択」に並ぶ別の劇場の `ticket_*.html`（東京・梅芸・フォーラム等）。
- 公演スケジュール `/schedule/index.html` は JavaScript で描く＝読まない（①②③で足りる）。
## チケットページの形
- `<title>チケット：宝塚大劇場 | 月組公演 『…』『…』 | 宝塚歌劇公式ホームページ</title>`
- 「会場を選択」の `<a class="active">宝塚大劇場 [兵庫県]</a>`＝この頁の劇場と県。
- `<p class="period">公演期間：2026年12月12日（土） - 2027年1月24日（日）</p>`
- 受付＝`<section class="article02">` ごと（`<h3>先行販売</h3>`・`<h3>一般前売　※11月21日（土）前売開始</h3>`）、
  その中の `<div class="set"><h4>宝塚友の会</h4><p class="txt">■「第1抽選方式」<br/>申込期間：10月3日（土）10:00〜…`
- 🚨電話番号が受付の欄に書いてある＝**行ごと落とす**（tmp/ は公開される）。
"""
import argparse
import datetime
import html as htmlmod
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'https://kageki.hankyu.co.jp'
# 🚨UA にメールアドレス・個人の情報を入れない（2026-11-11 Wikimedia の件）
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) OSHINAVI-harvest',
      'Accept-Language': 'ja,en;q=0.8'}
JST = datetime.timezone(datetime.timedelta(hours=9))
TICKET_RE = re.compile(r'href="(/revue/\d{4}/[\w\-]+/ticket_[\w\-]+\.html)')
SHOW_RE = re.compile(r'href="(/revue/\d{4}/[\w\-]+/index\.html)"')


def fetch(url, tries=3, sleep=3.0):
    """1ページ読むごとに sleep 秒あける。403/404/429 はそのまま上に投げる。確認画面が出たら止める。"""
    last = None
    for i in range(tries):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40)
            body = r.read().decode('utf-8', 'replace')
            time.sleep(sleep)
            if re.search(r'captcha|cf-chl|challenge-platform|ロボットではありません', body, re.I):
                raise RuntimeError('人間かどうかの確認画面が出た＝止める')
            return body
        except urllib.error.HTTPError as e:
            time.sleep(sleep)
            if e.code in (403, 404, 429):
                raise
            last = e
        except RuntimeError:
            raise
        except Exception as e:
            last = e
        time.sleep(sleep * (i + 2))
    raise last


EMAIL_RE = re.compile(r'[\w.+-]+@[\w-]+(?:\.[\w-]+)+')
TEL_RE = re.compile(r'TEL|ＴＥＬ|電話番号|\d{2,4}-\d{2,4}-\d{3,4}')


def lines_of(s):
    """HTML の切れ端 → 文字の行（<br> と </p> で割る）。電話番号・メールの行は落とす。"""
    s = re.sub(r'<br\s*/?>|</p>|</li>|</dd>', '\n', s or '', flags=re.I)
    s = re.sub(r'<[^>]+>', '', s)
    s = htmlmod.unescape(s).replace('　', ' ')
    out = []
    for ln in s.split('\n'):
        ln = re.sub(r'[ \t]+', ' ', ln).strip()
        if not ln or TEL_RE.search(ln) or EMAIL_RE.search(ln):
            continue
        out.append(ln)
    return out


def one_line(s):
    return ' '.join(lines_of(s))


def parse_ticket_page(h, url):
    """チケットページ → 公演の素（受付の文字は行のまま・組み立てで読む）。"""
    t = one_line((re.search(r'<title>(.*?)</title>', h, re.S) or [None, ''])[1])
    parts = [x.strip() for x in t.split('|')]
    show = parts[1] if len(parts) >= 3 else ''
    act = re.search(r'<a href="([^"]+)" class="active">(.*?)</a>', h, re.S)
    venue_txt = one_line(act.group(2)) if act else ''
    mv = re.match(r'(.*?)\s*\[([^\]]+)\]\s*$', venue_txt)
    others = sorted(set(TICKET_RE.findall(h)))
    period = one_line((re.search(r'<p class="period">(.*?)</p>', h, re.S) or [None, ''])[1])
    i = h.find('チケットお求め方法')
    body = h[i:] if i >= 0 else ''
    j = body.find('<footer')
    body = body[:j] if j > 0 else body
    sections = []
    for sec in re.split(r'<section class="article02">', body)[1:]:
        h3 = one_line((re.search(r'<h3>(.*?)</h3>', sec, re.S) or [None, ''])[1])
        sets = []
        for st in re.split(r'<div class="set">', sec)[1:]:
            h4 = one_line((re.search(r'<h4>(.*?)</h4>', st, re.S) or [None, ''])[1])
            rest = re.sub(r'<h4>.*?</h4>', '', st, flags=re.S)
            rest = re.sub(r'<div class="linkset2">.*?</div>', '', rest, flags=re.S)
            sets.append({'h4': h4, 'lines': lines_of(rest)[:30]})
        sections.append({'h3': h3, 'sets': sets})
    return {'url': url, 'page': url.split('#')[0], 'show': show, 'title_raw': t,
            'venue': mv.group(1).strip() if mv else venue_txt, 'venue_pref': mv.group(2) if mv else '',
            'period': period, 'sections': sections, 'other_pages': others,
            'troupe': (re.search(r'(花|月|雪|星|宙)組|専科', show) or [None])[0]}


def harvest(sleep=3.0, urls=None, log=print):
    pages, src = [], {}
    errs = []

    def add(u, how):
        u = urllib.parse.urljoin(BASE, u.split('#')[0])
        if u not in src:
            src[u] = how
            pages.append(u)

    if urls:
        for u in urls:
            add(u, 'urls')
    else:
        try:
            h = fetch(BASE + '/ticket/index.html', sleep=sleep)
            for u in TICKET_RE.findall(h):
                add(u, 'ticket_index')
            log('  チケット購入の一覧 → チケットページ %d' % len(pages))
        except Exception as e:
            errs.append({'url': '/ticket/index.html', 'error': str(e)[:160]})
        try:
            h = fetch(BASE + '/revue/index.html', sleep=sleep)
            shows = sorted(set(SHOW_RE.findall(h)))
            log('  公演案内 → 公演 %d' % len(shows))
            for s in shows:
                try:
                    hs = fetch(BASE + s, sleep=sleep)
                except Exception as e:
                    errs.append({'url': s, 'error': str(e)[:160]})
                    continue
                n = len(pages)
                for u in TICKET_RE.findall(hs):
                    add(u, 'revue')
                log('    %s → 新しいチケットページ %d' % (s, len(pages) - n))
        except Exception as e:
            errs.append({'url': '/revue/index.html', 'error': str(e)[:160]})
    rows, k = [], 0
    while k < len(pages):
        u = pages[k]
        k += 1
        try:
            h = fetch(u, sleep=sleep)
        except Exception as e:
            errs.append({'url': u, 'error': str(e)[:160]})
            log('  ❌ %s %s' % (u, str(e)[:60]))
            continue
        d = parse_ticket_page(h, u)
        d['found_by'] = src.get(u)
        rows.append(d)
        if not urls:
            for o in d['other_pages']:
                add(o, 'venue_select')
        log('  [%d] %s %s｜%s｜受付の欄 %d' % (k, u.replace(BASE, ''), d['show'][:24], d['venue'],
                                          sum(len(s['sets']) for s in d['sections'])))
    return rows, errs


def _selftest():
    h = '''<title>チケット：宝塚大劇場 | 月組公演 『天穹のアルテミス』『Belle &Eacute;poque』 | 宝塚歌劇公式ホームページ</title>
<ul><li><a href="/revue/2026/x/ticket_takarazuka.html" class="active"> 宝塚大劇場 [兵庫県] </a></li>
<li><a href="/revue/2026/x/ticket_tokyo.html"> 東京宝塚劇場 [東京都] </a></li></ul>
<p class="period">公演期間：2026年12月12日（土） - 2027年1月24日（日）</p>
<section class="article01"><h2>チケットお求め方法</h2></section>
<section class="article02"><h3>先行販売</h3><div class="set"><h4>宝塚友の会</h4><p class="txt">一般前売に先がけて<br/><br/>
<strong>■「第1抽選方式」</strong><br/> 申込期間：10月3日（土）10:00〜10月4日（日）23:00<br/> 結果照会：10月7日（水）10:00〜</p>
<div class="linkset2"><ul><li><a href="https://www.takarazuka-ticket.com/">Webチケットサービス</a></li></ul></div></div></section>
<section class="article02"><h3>一般前売　※11月21日（土）前売開始</h3><div class="set"><h4>宝塚大劇場・電話受付</h4>
<p class="txt">11月24日（火）朝10時から<br/>TEL．0570-00-0000（10:00〜18:00）<br/>a@b.cc</p></div></section><footer>x</footer>'''
    d = parse_ticket_page(h, 'https://kageki.hankyu.co.jp/revue/2026/x/ticket_takarazuka.html')
    assert d['show'] == '月組公演 『天穹のアルテミス』『Belle Époque』' and d['troupe'] == '月組', d['show']
    assert d['venue'] == '宝塚大劇場' and d['venue_pref'] == '兵庫県'
    assert d['period'] == '公演期間：2026年12月12日（土） - 2027年1月24日（日）'
    assert d['other_pages'] == ['/revue/2026/x/ticket_takarazuka.html', '/revue/2026/x/ticket_tokyo.html']
    assert d['sections'][0]['h3'] == '先行販売' and d['sections'][0]['sets'][0]['h4'] == '宝塚友の会'
    assert d['sections'][0]['sets'][0]['lines'] == ['一般前売に先がけて', '■「第1抽選方式」',
                                                   '申込期間：10月3日（土）10:00〜10月4日（日）23:00',
                                                   '結果照会：10月7日（水）10:00〜'], d['sections'][0]['sets'][0]['lines']
    s2 = json.dumps(d['sections'][1], ensure_ascii=False)
    assert '0570' not in s2 and '@' not in s2 and '11月24日（火）朝10時から' in s2, s2
    print('selftest OK: 題・劇場と県・会期・受付の欄（h3/h4/行）/電話番号とメールの行を落とす/別の劇場のページ')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='tmp/takarazuka_harvest.json')
    ap.add_argument('--sleep', type=float, default=3.0)
    ap.add_argument('--urls', default='', help='チケットページ（/revue/…/ticket_*.html）を名指し・カンマ区切り')
    ap.add_argument('--today', default=datetime.datetime.now(JST).date().isoformat())
    a = ap.parse_args([x for x in sys.argv[1:] if x != '--selftest'])
    rows, errs = harvest(a.sleep, [u.strip() for u in a.urls.split(',') if u.strip()] or None)
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    json.dump({'today': a.today, 'events': rows, 'errors': errs},
              io.open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('\n=== チケットページ %d / 読めなかった %d → %s ===' % (len(rows), len(errs), a.out))


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        _selftest()
        sys.exit(0)
    main()
