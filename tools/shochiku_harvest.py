# -*- coding: utf-8 -*-
"""チケットWeb松竹（www1.ticket-web-shochiku.com・歌舞伎ほか）の公演を集める。

  python tools/shochiku_harvest.py --out tmp/x1120/newv/shochiku/harvest.json
  python tools/shochiku_harvest.py --selftest

## 規約・robots（2026-11-20 に読んだ）
- 規約（/t/info/rules.html）はすちこが確認済み＝ボットの条文なし、または購入用ボットの禁止だけ。
- robots.txt は無い（404）。**申込・ログインは一切しない・1ページごとに3秒以上あける・同時に1本だけ**。
- 公演の紹介文・注意書きは**写さない**（公演名・会期・劇場・住所の県・発売日の事実だけ）。

## 一覧の取り方（2026-11-20 実測）
- 購入の画面（/tticket/thsel.do）は JavaScript で POST する作り（合言葉つき）＝機械では読まない。
- 読むのは「発売日スケジュール」の静的 HTML 2枚＝東 `/t/info/sale_schedule_east.html`・西 `/t/info/sale_schedule_west.html`
  （入口 `/t/info/schedule.html`）。文字コードは UTF-8。
- 形：劇場ごとの見出し `<h4 class="page-block__title" id="boxN">劇場名<br><span>住所</span></h4>`
  → その下に公演ごとの `<div class="performance__body">`：
  `<h4 class="performance-title">公演名</h4>`・`<p class="… agenda_size"><strong>会期</strong></p>`・
  販売方法のアイコン（`<span class="web|tel|madoguchi icon_size">`）・
  発売日の表（`<th>受付の名前</th><td>M月D日（曜）～</td>`）。
- 🚨古い公演は `<!-- … -->` で隠してある＝**コメントを外してから読む**（外さないと終わった公演が出る）。
- 🚨表の HTML が崩れている所がある（`<th>…</td>`・`</tr<tr>`）＝閉じタグを当てにせず、行（`<tr`）で割って読む。
- 発売日の表には**年が無い**・**終わりが無い**（「10月14日（水）～」）。年は組み立て側で曜日と会期から1つに決める。
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
import urllib.request

if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'https://www1.ticket-web-shochiku.com/t/info/'
PAGES = (('east', BASE + 'sale_schedule_east.html'), ('west', BASE + 'sale_schedule_west.html'))
# 🚨UA にメールアドレス・個人の情報を入れない（2026-11-11 Wikimedia の件）
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) OSHINAVI-harvest',
      'Accept-Language': 'ja,en;q=0.8'}
JST = datetime.timezone(datetime.timedelta(hours=9))


def fetch(url, tries=3, sleep=3.0):
    """1ページ読むごとに sleep 秒あける。403/404 はそのまま上に投げる（人間の確認・門で断られた時は止める）。"""
    last = None
    for i in range(tries):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40)
            raw = r.read()
            time.sleep(sleep)
            cs = (re.search(r'charset=([\w-]+)', r.headers.get('Content-Type') or '') or [None, 'utf-8'])[1]
            body = raw.decode('cp932' if cs.lower() in ('shift_jis', 'sjis', 'x-sjis') else cs, 'replace')
            if re.search(r'captcha|recaptcha|cf-chl|challenge-platform|ロボットではありません', body, re.I):
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


def text_of(s):
    """タグを外して1行にする（<br> は空白）。"""
    s = re.sub(r'<br\s*/?>', ' ', s or '', flags=re.I)
    s = re.sub(r'<[^>]+>', '', s)
    s = htmlmod.unescape(s).replace('　', ' ')
    return re.sub(r'\s+', ' ', s).strip()


def strip_comments(h):
    return re.sub(r'<!--.*?-->', '', h, flags=re.S)


def table_rows(body):
    """発売日の表 → [(受付の名前, 日付の文字)]。閉じタグを当てにせず <tr で割る。"""
    out = []
    for tb in re.findall(r'<table[^>]*>(.*?)</table>', body, re.S):
        for tr in re.split(r'<tr\b', tb)[1:]:
            m = re.search(r'<th[^>]*>(.*?)(?=<td|</tr|$)', tr, re.S)
            d = re.search(r'<td[^>]*>(.*?)(?=</td|<tr|</tr|<th|$)', tr, re.S)
            if m and d:
                out.append((text_of(m.group(1)), text_of(d.group(1))))
    return out


NO_WEB_RE = re.compile(r'チケットWeb松竹での販売はございません')


def parse_page(h, region, page_url):
    """発売日スケジュールの HTML → 公演のリスト。"""
    h = strip_comments(h)
    parts = re.split(r'(<h4 class="page-block__title[^"]*"[^>]*>.*?</h4>)', h, flags=re.S)
    events = []
    for i in range(1, len(parts), 2):
        head = parts[i]
        box = (re.search(r'id="(box\d+)"', head) or [None, ''])[1]
        addr = text_of((re.search(r'<span>(.*?)</span>', head, re.S) or [None, ''])[1])
        theater = text_of(re.sub(r'<span>.*?</span>', '', head, flags=re.S))
        body = parts[i + 1]
        blocks = re.split(r'(?=<h4 class="performance-title)', body)
        n = 0
        for b in blocks:
            mt = re.match(r'<h4 class="performance-title[^"]*"[^>]*>(.*?)</h4>', b, re.S)
            if not mt:
                continue
            n += 1
            title = text_of(mt.group(1))
            span = text_of((re.search(r'agenda_size[^>]*>(.*?)</p>', b, re.S) or [None, ''])[1])
            meth = re.search(r'販売方法</span>(.*?)</p>', b, re.S)
            methods = re.findall(r'<span class="(\w+) icon_size">', meth.group(1)) if meth else []
            static = (re.search(r'class="static-text"(.*)', b, re.S) or [None, ''])[1]
            events.append({
                'region': region, 'page': page_url, 'box': box, 'n': n,
                'url': '%s#%s' % (page_url, box) if box else page_url,
                'key': '%s#%s|%s' % (region, box, title),
                'theater': theater, 'address': addr, 'title': title, 'span': span,
                'methods': methods,
                'kabukikai': bool(re.search(r'shochikukabukikai icon_size', b)),
                'rows': table_rows(b),
                # 注意書きは写さない＝「Web松竹では売らない」の一文があるかだけ
                'no_web_note': bool(NO_WEB_RE.search(text_of(static))),
            })
    return events


def harvest(sleep=3.0, log=print):
    rows, errs = [], []
    for region, url in PAGES:
        try:
            h = fetch(url, sleep=sleep)
        except Exception as e:
            errs.append({'url': url, 'error': str(e)[:160]})
            log('  ❌ %s 読めない: %s' % (url, str(e)[:80]))
            continue
        evs = parse_page(h, region, url)
        log('  %s 公演 %d件（劇場 %d）' % (region, len(evs), len({e['box'] for e in evs})))
        rows += evs
    return rows, errs


def _selftest():
    h = '''<h4 class="page-block__title title3 s-mt1" id="box1">歌舞伎座<br><span>東京都中央区銀座4-12-15</span></h4>
<div class="performance__body"><div class="performance__body">
<h4 class="performance-title title_margin"><span style="font-size: 12px;"><br></span> 吉例顔見世大歌舞伎 </h4>
<p class="mt1 md agenda_size"><strong>2026年11月1日（日）～11月25日（水）</strong></p>
<ul><li><p class="md icon_list"><span class="li_line">松竹歌舞伎会</span><span class="shochikukabukikai icon_size">松竹歌舞伎会</span></p></li>
<li><p class="md icon_list"><span class="li_line">販売方法</span><span class="web icon_size">Web</span><span class="tel icon_size">電話</span></p></li></ul>
<table class="page-block__table"><tr><th class="width-auto">「松竹歌舞伎会」ゴールド会員</th><td>10月11日（日）～</span></td></tr>
<tr><th class="width-auto">一般販売<br></th><td>10月14日（水）～</td></tr
<tr><th class="width-auto">窓口販売・お引き取り</td><td>10月16日（金）～</td></tr></table>
<div class="static-text"><p>※問い合わせ 03-0000-0000 長い注意書き</p></div></div>
<!-- <h4 class="performance-title">終わった公演</h4><p class="agenda_size"><strong>2020年1月1日</strong></p> -->
</div>
<h4 class="page-block__title title3 s-mt1" id="box56">博多座<br><span>福岡市博多区下川端町2-1</span></h4>
<div class="performance__body"><h4 class="performance-title">流白浪燦星<br>碧翠の麗城<br></h4>
<p class="mt1 md agenda_size"><strong>2027年2月6日（土）～2月26日（金）</strong></p>
<p class="md icon_list"><span class="li_line">販売方法</span><span class="web icon_size">Web</span></p>
<table><tr><th>一般販売</th><td>12月5日（土）～</td></tr></table>
<div class="static-text"><p>※チケットWeb松竹での販売はございません</p></div></div>'''
    evs = parse_page(h, 'east', 'https://x/east.html')
    assert [e['title'] for e in evs] == ['吉例顔見世大歌舞伎', '流白浪燦星 碧翠の麗城'], evs
    e = evs[0]
    assert e['theater'] == '歌舞伎座' and e['address'] == '東京都中央区銀座4-12-15' and e['box'] == 'box1'
    assert e['span'] == '2026年11月1日（日）～11月25日（水）' and e['methods'] == ['web', 'tel'] and e['kabukikai']
    assert e['rows'] == [('「松竹歌舞伎会」ゴールド会員', '10月11日（日）～'), ('一般販売', '10月14日（水）～'),
                         ('窓口販売・お引き取り', '10月16日（金）～')], e['rows']
    assert e['url'] == 'https://x/east.html#box1' and e['key'] == 'east#box1|吉例顔見世大歌舞伎'
    assert '03-' not in json.dumps(evs, ensure_ascii=False) and not e['no_web_note'] and evs[1]['no_web_note']
    assert evs[1]['theater'] == '博多座' and evs[1]['rows'] == [('一般販売', '12月5日（土）～')]
    print('selftest OK: コメントを外す/崩れた表を行で読む/劇場・住所・会期・販売方法/注意書きを写さない')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='tmp/shochiku_harvest.json')
    ap.add_argument('--sleep', type=float, default=3.0)
    ap.add_argument('--today', default=datetime.datetime.now(JST).date().isoformat())
    a = ap.parse_args([x for x in sys.argv[1:] if x != '--selftest'])
    rows, errs = harvest(a.sleep)
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    json.dump({'today': a.today, 'events': rows, 'errors': errs},
              io.open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('\n=== 公演 %d件 / 読めなかったページ %d → %s ===' % (len(rows), len(errs), a.out))


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        _selftest()
        sys.exit(0)
    main()
