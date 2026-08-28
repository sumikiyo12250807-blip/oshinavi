# -*- coding: utf-8 -*-
"""ぴあをキーワードで総ざらいして、そのアーティスト/公演名の**全販売枠**を列挙する。

【なぜ要るか】
- `search_all.do`（ユーザーが見る検索画面）と `artist/artists.do` は **JS駆動で生HTMLに公演が1件も出ない**
  （2026-07-30実測：search_all=70KBでevent.do 0本／artists.do=82KBで0本）。
- ところが **`/pia/rlsInfo.do?kw=<語>` はサーバー側でHTMLを返す**（同日発見）。
  発売前ハーベスタ([[reference_pia_presale_api]])と同じ形式なので同じパーサが使える。
- これで [[feedback_harvest_name_dedup_blindspot]]（既存artist名で除外するので**同名の別公演を
  永久に拾えない**）と [[feedback_tour_cross_channel_blindspot]] の取りこぼしを、
  アーティスト単位で潰せる。LINDBERG/工藤静香/玉置浩二と同じ「1公演しか持っていない」型の発見に使う。

使い方:
  python tools/pia_kw_search.py マカロニえんぴつ
  python tools/pia_kw_search.py マカロニえんぴつ --out tmp/kw_macaroni.txt
  python tools/pia_kw_search.py --selftest

出力はUTF-8ファイル（コンソールに日本語を出さない＝化け読み事故防止 [[feedback_no_mojibake_japanese_read]]）。
状態は「発売前 / 受付中 / 発売中」等ぴあの status_icon_text をそのまま出す（推測しない）。
"""
import html as H
import io
import re
import sys
import time
import urllib.parse
import urllib.request

UA = {'User-Agent': 'Mozilla/5.0'}
# 無フィルタ＝全状態。加えて各フィルタでも引いて union する（ぴあは既定で一部しか返さないことがある）。
# 🚨2026-08-27 修正＝rlsIn は「発売までの日数の窓」で最大30日しか無く、
#   31日より先に発売される枠を1つも返さない（[[reference_pia_rlsin_measured]]）。
#   発売前は rlsStatus=0102(先着)／0202(抽選) が正しい（[[reference_pia_presale_full_filter]]）。
FILTERS = ['', 'rlsStatus=0101', 'rlsStatus=0102', 'rlsStatus=0201', 'rlsStatus=0202']


def strip(s):
    return H.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s))).strip()


def fetch(kw, filt, page, tries=3):
    q = 'kw=%s' % urllib.parse.quote(kw)
    if filt:
        q += '&' + filt
    url = 'https://t.pia.jp/pia/rlsInfo.do?%s&page=%d' % (q, page)
    last = None
    for i in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode('utf-8', 'replace')
        except Exception as e:
            last = e
            time.sleep(2.0 * (i + 1))
    raise last


def parse_page(h):
    """presale_harvest.parse_page と同じ構造（rlsInfo.do の listWrp_title_list を1件ずつ）"""
    out = []
    for body in re.split(r'(?=<li class="listWrp_title_list clearfix">)', h):
        am = re.search(r'<a href="([^"]*event\.do\?event(?:Bundle)?Cd=\w+)"[^>]*>(.*?)</a>', body, re.S)
        if not am:
            continue

        def span(cls):
            m = re.search(r'<span class="%s">(.*?)</span>\s*(?=<span class="list_|<span class="add_alert|</li>)' % cls, body, re.S)
            return strip(m.group(1)) if m else ''

        st = re.search(r'status_icon_text[^>]*>(.*?)</span>', body, re.S)
        # 発売日欄の3パターン（presale_harvest.py と同じ。2026-08-29 実HTMLで確認）
        SEP = r'(?:</?[a-zA-Z][^>]*>|\s)*'
        rm = re.search(r'発売前' + SEP + r'(\d{4}/\d{1,2}/\d{1,2})', body)
        lm = re.search(r'(?:まもなく|近日)抽選受付' + SEP + r'(\d{4}/\d{1,2}/\d{1,2})', body)
        if rm:
            _rls = rm.group(1)
        elif re.search(r'本日発売' + SEP + r'\(' + SEP + r'発売前' + SEP + r'\)', body):
            _rls = 'TODAY'
        else:
            _rls = lm.group(1) if lm else ''
        out.append({
            'url': am.group(1).replace('http://', 'https://'),
            'title': strip(am.group(2)),
            'status': strip(st.group(1)) if st else '',
            'rlsdate': _rls,
            'perfdate': span('list_03'),
            'venue': span('list_04'),
        })
    return out


def search(kw, log=None):
    """キーワードで全フィルタ×全ページを走査し、URL単位で union して返す"""
    found = {}
    for filt in FILTERS:
        seen_here, page, empty = set(), 1, 0
        while page <= 60:
            try:
                items = parse_page(fetch(kw, filt, page))
            except Exception as e:
                if log is not None:
                    log.append('  ! %s page%d fetch失敗 %s' % (filt or '(無)', page, type(e).__name__))
                break
            fresh = [x for x in items if x['url'] not in seen_here]
            # ぴあは範囲外ページで最後のページを返す＝「新規URLが増えない」で終端判定
            # （[[reference_pia_pagination_overrun]]）
            if not fresh:
                empty += 1
                if empty >= 2:
                    break
            else:
                empty = 0
                for x in fresh:
                    seen_here.add(x['url'])
                    prev = found.get(x['url'])
                    if prev is None:
                        x['filters'] = [filt or '(無)']
                        found[x['url']] = x
                    else:
                        prev['filters'].append(filt or '(無)')
            page += 1
            time.sleep(0.4)
        if log is not None:
            log.append('  %-14s → %d件' % (filt or '(無フィルタ)', len(seen_here)))
    return found


SELFTEST_HTML = '''
<li class="listWrp_title_list clearfix"><a href="http://t.pia.jp/pia/event/event.do?eventCd=2621851">
マカロニえんぴつ</a><span class="status_icon_text">発売前</span>発売前 2026/08/03
<span class="list_03">2026/10/31(土)</span><span class="list_04">真駒内セキスイハイムアイスアリーナ(北海道)</span></li>
<li class="listWrp_title_list clearfix"><a href="http://t.pia.jp/pia/event/event.do?eventBundleCd=b2668571">
マカロニえんぴつ TOUR</a><span class="status_icon_text">受付中</span>
<span class="list_03">2026/11/07(土)</span><span class="list_04">Zepp Sapporo(北海道)</span></li>
'''


def selftest():
    got = parse_page(SELFTEST_HTML)
    assert len(got) == 2, got
    assert got[0]['url'].endswith('eventCd=2621851'), got[0]
    assert got[0]['status'] == '発売前', got[0]
    assert got[0]['rlsdate'] == '2026/08/03', got[0]
    assert got[0]['perfdate'] == '2026/10/31(土)', got[0]
    assert '真駒内' in got[0]['venue'], got[0]
    assert got[1]['url'].endswith('eventBundleCd=b2668571'), got[1]
    assert got[1]['status'] == '受付中', got[1]
    assert got[1]['rlsdate'] == '', got[1]
    # 陽性テスト：event.doリンクが無いliは拾わない
    assert parse_page('<li class="listWrp_title_list clearfix">ゴミ</li>') == []
    print('selftest OK (2 cases + negative)')


def main():
    a = sys.argv[1:]
    if '--selftest' in a:
        return selftest()
    if not a:
        print('usage: python tools/pia_kw_search.py <keyword> [--out path]')
        return 1
    kw = a[0]
    out = a[a.index('--out') + 1] if '--out' in a else 'tmp/pia_kw_search.txt'
    log = ['検索語: %s' % kw, '']
    found = search(kw, log)
    log.append('')
    log.append('=== ヒット %d 件（URL単位・全フィルタのunion）===' % len(found))
    for u, x in sorted(found.items(), key=lambda kv: (kv[1]['perfdate'], kv[0])):
        log.append('')
        log.append('[%s] %s' % (x['status'] or '状態不明', x['title']))
        log.append('  公演日: %s' % (x['perfdate'] or '(空)'))
        log.append('  会場  : %s' % (x['venue'] or '(空)'))
        if x['rlsdate']:
            log.append('  発売日: %s' % x['rlsdate'])
        log.append('  URL   : %s' % u)
        log.append('  検出フィルタ: %s' % ','.join(x['filters']))
    io.open(out, 'w', encoding='utf-8').write('\n'.join(log) + '\n')
    print('wrote %s (%d events)' % (out, len(found)))
    return 0


if __name__ == '__main__':
    sys.exit(main() or 0)
