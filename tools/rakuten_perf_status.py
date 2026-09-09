# -*- coding: utf-8 -*-
"""楽天チケットの「公演ごとの売り状態」を取る（購入する／予定枚数終了 など）。

  python tools/rakuten_perf_status.py <楽天のURL> [--json out.json]
  python tools/rakuten_perf_status.py --selftest

## なぜ要るか（2026-09-10 ユーザーが画面で発見）

ユーザー「**木下グループが売り切れ出てる　売り切れで表示してね**」。
調べたら id7494 ジャパンオープンは 14公演中 **12公演が「予定枚数終了」**なのに、
OSHINAVI は全部「買える枠」として出していた。

🚨真因＝**楽天の売り状態は生HTMLに1文字も無い**。
   ・公演カードの class は売り切れても `active` のまま
   ・購入ボタンは `<div class='column-5 performance_btn perf_3' data-perf='3'>...</div>` の
     プレースホルダで、中身は**後からAJAXで差し込まれる**
   ＝`rakuten_harvest.parse_perfs` の `status`（class から読む）は
     「販売期間が終わったか」しか見ておらず、**売り切れを検知できない**。
   2026-09-08 に「楽天は予定枚数終了と販売終了を書き分けていない」と結論したのは、
   **生HTMLしか見ていなかったから**＝この道具で覆る（[[project_rakuten_make_it_ironclad]]③を更新）。

## どこから取るか

ページのインラインJSに呼び出しがそのまま書いてある:

    let ecd = "RTEP928";
    jQuery.post("https://cms-api.ticket.rakuten.co.jp/coreui/ajax/performance/widget",
                {"ids": "1,2,3,...", "ecd": ecd, "eid": "1103076"}, ...)

返りは `[{"perf_1": "<a ...>購入する</a>"}, {"perf_2": "..."}]` の形。
`ecd` と `eid` は生HTMLから正規表現で取れるので、**実ブラウザ無しで取れる**。
"""
import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')

API = 'https://cms-api.ticket.rakuten.co.jp/coreui/ajax/performance/widget'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'

# PC側の公演カード（perf番号つき）。モバイル用カードは data-perf を持たないので混ざらない。
CARD_PERF = re.compile(
    r"<div class='performance(?P<state>[^']*)' data-date='(?P<dd>\{[^']*\})'>(?P<body>.*?)"
    r"data-perf='(?P<perf>\d+)'", re.S)
COL = re.compile(r"<div class='column-(?P<n>\d)'>(?P<v>.*?)</div>", re.S)


def strip_tags(s):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s or '')).strip()


def fetch(u, timeout=40):
    req = urllib.request.Request(u, headers={'User-Agent': UA})
    return urllib.request.urlopen(req, timeout=timeout).read().decode('utf-8', 'replace')


def parse_cards(body):
    """(perf番号, 公演日, 開演時刻, エリア, 会場, 券種名, 販売終了日時) を順に返す。"""
    out = []
    for m in CARD_PERF.finditer(body):
        cols = {int(c.group('n')): strip_tags(c.group('v')) for c in COL.finditer(m.group('body'))}
        d = re.search(r'(20\d{2})年\s*(\d{1,2})月\s*(\d{1,2})日', cols.get(6, ''))
        if not d:
            continue
        try:
            dd = json.loads(m.group('dd'))
        except Exception:
            dd = {}
        t = re.search(r'開演\s*(\d{1,2}:\d{2})', cols.get(2, ''))
        out.append({
            'perf': m.group('perf'),
            'date': '%s-%02d-%02d' % (d.group(1), int(d.group(2)), int(d.group(3))),
            'time': t.group(1) if t else '',
            'pref': cols.get(3, ''),
            'venue': cols.get(4, ''),
            'ticket_name': cols.get(1, ''),
            'sale_end': (dd.get('max_end_on') or '').replace('T', ' ')[:16],
            'card_state': m.group('state').strip(),
        })
    return out


def parse_keys(body):
    """AJAXに渡す ecd（イベントコード）と eid を生HTMLから取る。"""
    ecd = re.search(r'let\s+ecd\s*=\s*"([^"]+)"', body)
    eid = re.search(r'"eid"\s*:\s*"(\d+)"', body)
    return (ecd.group(1) if ecd else None), (eid.group(1) if eid else None)


def ask_api(ids, ecd, eid, timeout=40, tries=3):
    """🚨連続で叩くと空/非JSONが返る。**間を空けて必ず数回試す**。
    ここを1回で諦めると「売り切れが分からない」を「売り切れていない」と読み違える
    （[[reference_pia_rate_limit_429]] と同型＝失敗は"死んだ"ではなく"確かめられなかった"）。"""
    last = None
    for i in range(tries):
        if i:
            time.sleep(2.5 * i)
        try:
            return _ask_api_once(ids, ecd, eid, timeout)
        except Exception as ex:
            last = ex
    raise last


def _ask_api_once(ids, ecd, eid, timeout=40):
    data = urllib.parse.urlencode({'ids': ','.join(ids), 'ecd': ecd, 'eid': eid}).encode()
    # 🚨X-Requested-With と Accept を付けないとJSONで返ってこない（2026-09-10 実測）
    req = urllib.request.Request(API, data=data, headers={
        'User-Agent': UA,
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://ticket.rakuten.co.jp',
        'Referer': 'https://ticket.rakuten.co.jp/',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
    })
    return json.loads(urllib.request.urlopen(req, timeout=timeout).read().decode('utf-8', 'replace'))


SOLD = re.compile(r'予定枚数終了|完売|売切|売り切れ|SOLD\s*OUT', re.I)
BUY = re.compile(r'購入|申込|申し込み|抽選')


def status_of(label):
    """ボタンの文字を3つに畳む。分からないものは 'unknown'（黙って合格にしない）。"""
    if not label:
        return 'unknown'
    if SOLD.search(label):
        return 'soldout'
    if BUY.search(label):
        return 'buyable'
    return 'unknown'


def perf_status(url, timeout=40):
    """楽天のイベントURL → 公演ごとの売り状態のリスト。"""
    body = fetch(url, timeout)
    cards = parse_cards(body)
    ecd, eid = parse_keys(body)
    if not cards or not ecd or not eid:
        return {'url': url, 'ok': False, 'why': '公演カード/ecd/eidが取れない形式', 'rows': []}
    res = ask_api([c['perf'] for c in cards], ecd, eid, timeout)
    label, href = {}, {}
    for item in res or []:
        for k, v in (item or {}).items():
            label[k] = strip_tags(v)
            # 🎯返りには**その公演だけの購入URL**が入っている。
            #   生HTMLには飛び先が無いので「米子の昼だけ押させる」にはこれが要る
            #   （2026-09-10 朝に「実ブラウザでないと取れない」と書いたのは誤り＝ここで取れる）。
            hm = re.search(r'href="([^"]+)"', v or '')
            if hm:
                href[k] = hm.group(1).replace('\\/', '/')
    for c in cards:
        c['button'] = label.get('perf_' + c['perf'], '')
        c['buy_url'] = href.get('perf_' + c['perf'], '')
        c['status'] = status_of(c['button'])
    return {'url': url, 'ok': True, 'ecd': ecd, 'eid': eid, 'rows': cards}


def _selftest():
    assert status_of('予定枚数終了') == 'soldout'
    assert status_of('購入する') == 'buyable'
    assert status_of('SOLD OUT') == 'soldout'
    assert status_of('抽選申込') == 'buyable'
    assert status_of('') == 'unknown'
    assert status_of('受付終了') == 'unknown'      # 売り切れとは言い切れない＝弱いほうに倒す
    body = ("<div class='performance active' data-date='{\"max_end_on\":\"2026-09-24T23:59:59\"}'>"
            "<div class='column-1'>セッション1</div>"
            "<div class='column-6'>2026年 09月 30日 (水)</div>"
            "<div class='column-2'>開場 09:30 / 開演 11:00</div>"
            "<div class='column-3'>東京都</div>"
            "<div class='column-4'>有明コロシアム</div>"
            "<div class='column-5 performance_btn perf_3' data-perf='3'>...</div></div>"
            'let ecd = "RTEP928";  "eid": "1103076"')
    cards = parse_cards(body)
    assert len(cards) == 1 and cards[0]['perf'] == '3', cards
    assert cards[0]['date'] == '2026-09-30' and cards[0]['time'] == '11:00', cards
    assert cards[0]['sale_end'] == '2026-09-24 23:59', cards
    assert parse_keys(body) == ('RTEP928', '1103076')
    print('selftest OK: 売り状態の畳み方 / 公演カード(perf番号つき) / ecd・eidの取り出し')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('url', nargs='?')
    ap.add_argument('--json', default='')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        _selftest()
        return 0
    r = perf_status(a.url)
    if not r['ok']:
        print('⏭️ %s（%s）' % (r['url'], r['why']))
        return 2
    print('%s  ecd=%s eid=%s  公演%d件' % (r['url'], r['ecd'], r['eid'], len(r['rows'])))
    for c in r['rows']:
        print('  %s %-5s %-24s %-10s %s'
              % (c['date'], c['time'], c['venue'][:24], c['status'], c['button'][:20]))
    n = sum(1 for c in r['rows'] if c['status'] == 'soldout')
    print('  → 売り切れ %d / 買える %d / 不明 %d'
          % (n, sum(1 for c in r['rows'] if c['status'] == 'buyable'),
             sum(1 for c in r['rows'] if c['status'] == 'unknown')))
    if a.json:
        json.dump(r, open(a.json, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return 0


if __name__ == '__main__':
    sys.exit(main())
