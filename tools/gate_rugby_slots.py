# -*- coding: utf-8 -*-
"""TicketRugby 由来の枠の番人＝**チケット発売情報のページを読み直して、組み立てとは別の読み方で枠を作り、登録と全件突合**する。

  python tools/gate_rugby_slots.py                          … index.html の TicketRugby 枠を全部照合
  python tools/gate_rugby_slots.py --ids 1,2                … id 指定
  python tools/gate_rugby_slots.py --built tmp/x1120/newv/rugby/built.json   … 投入前の組み上がりを照合
  python tools/gate_rugby_slots.py --selftest

終了コード 0＝全一致 / 2＝食い違い・読めない あり。報告の形は「🚨 id=<番号> 名前」。

## 組み立て（rugby_harvest＋build_rugby_entries）と**別に**作る
- 組み立ては HTML の**クラス名**（game_seat_blk・game_seat_status・<th>販売期間</th>）で区切って読む。
  番人はページを**文字の並び**に直し（タグを消して、空席の印の画像だけ「⟦印N⟧」の札に置き換える）、
  「⟦印N⟧ 受付名 値段 販売期間 開始～終わり」の並びを拾う＝クラス名が変わっても組み立てと同じ間違いをしない。
- 試合日・開始・会場・県も、一覧ではなく**この発売情報のページの頭**から読む（組み立ては一覧から読む）。
- 日時の読み・状態の判定・締切を試合日で締める・バッジの文字を**ここで書き直している**（組み立ての関数は使わない）。
- バッジの文字を読み戻して（受付名・県・試合日・開始・発売日時・締切・売り切れ）比べる。
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
import unicodedata
import urllib.request

if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
REPORT = 'tmp/gate_rugby_report.txt'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
URL_RE = re.compile(r'ticketrugby\.jp/ticket_release_info/(\d+)')
PREFS = ('北海道 青森 岩手 宮城 秋田 山形 福島 茨城 栃木 群馬 埼玉 千葉 東京 神奈川 新潟 富山 石川 福井 山梨 長野 '
         '岐阜 静岡 愛知 三重 滋賀 京都 大阪 兵庫 奈良 和歌山 鳥取 島根 岡山 広島 山口 徳島 香川 愛媛 高知 福岡 佐賀 '
         '長崎 熊本 大分 宮崎 鹿児島 沖縄').split()
_OP = []
_LAST = [0.0]


def get(url, sleep):
    if not _OP:
        op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        op.addheaders = [('User-Agent', UA), ('Accept-Language', 'ja')]
        _OP.append(op)
    w = sleep - (time.time() - _LAST[0])
    if w > 0:
        time.sleep(w)
    _LAST[0] = time.time()
    t = _OP[0].open(url, timeout=60).read().decode('utf-8', 'replace')
    if re.search(r'captcha|cf-challenge|challenge-platform', t, re.I):
        raise RuntimeError('人間かどうかの確認画面')
    return t


def flat(t):
    """ページ → 1行の文字（空席の印の画像は ⟦印N⟧ の札に）。凡例（game_sec_r_infoli）は落とす。"""
    t = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', t, flags=re.S)
    t = re.sub(r'<ul class="game_sec_r_infoli">.*?</ul>', ' ', t, flags=re.S)
    t = re.sub(r'<img[^>]*ico_st(\d)[^>]*>', lambda m: ' ⟦印%s⟧ ' % m.group(1), t)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = H.unescape(t).replace('　', ' ')
    return re.sub(r'\s+', ' ', t)


WIN_RE = re.compile(r'⟦印(\d)⟧ ([^⟦]+?) [\d,]+円(?: ?[～〜] ?[\d,]+円)? 販売期間 '
                    r'(\d{4})/(\d{1,2})/(\d{1,2})\([^)]*\) (\d{1,2}):(\d\d) ?[～〜]'
                    r'(?: ?(\d{4})/(\d{1,2})/(\d{1,2})\([^)]*\) (\d{1,2}):(\d\d))?')


def page_info(t):
    f = flat(t)
    i = f.find('チケット発売情報')
    if i < 0:
        raise ValueError('チケット発売情報のページではない')
    top = f[i:i + 600]
    m = re.search(r'(\d{4})\. ?(\d{1,2})\.(\d{1,2})', top)
    day = '%s-%02d-%02d' % (m.group(1), int(m.group(2)), int(m.group(3))) if m else None
    m = re.search(r'開始 (\d{1,2}):(\d\d)', top)
    tm = '%d:%s' % (int(m.group(1)), m.group(2)) if m else None
    # 会場名の中にカッコがある型（「ヤマハスタジアム（磐田）（静岡県）」）＝最後の（県）までを会場名にする
    m = re.search(r'(?:\d{1,2}:\d\d|[月火水木金土日]) ((?:(?!開場|開始|⟦).)+?)（([^（）]{2,4}?(?:都|道|府|県))）', top)
    venue, pref = (zen2han(m.group(1)), m.group(2)) if m else ('', '')
    wins = []
    for m in WIN_RE.finditer(f):
        g = m.groups()
        st = datetime.datetime(int(g[2]), int(g[3]), int(g[4]), int(g[5]), int(g[6]))
        en = datetime.datetime(int(g[7]), int(g[8]), int(g[9]), int(g[10]), int(g[11])) if g[7] else None
        wins.append((g[1].strip(), st, en, int(g[0])))
    return {'day': day, 'time': tm, 'venue': venue, 'pref': pref, 'wins': wins}


def norm_name(s):
    """受付名を画面のバッジの書き方に（組み立てとは別に書く：NFKC のあと 半角カッコ・<>・[] を全角に）"""
    s = re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', s or '')).strip()
    for a, b in (('(', '（'), (')', '）'), ('[', '［'), (']', '］'), ('<', '＜'), ('>', '＞')):
        s = s.replace(a, b)
    return s


def zen2han(s):
    """全角の英数字と「－＆．」だけ半角に（カッコ・【】は残す）＝会場名の比べ方"""
    out = []
    for ch in s or '':
        o = ord(ch)
        if 0xFF10 <= o <= 0xFF19 or 0xFF21 <= o <= 0xFF3A or 0xFF41 <= o <= 0xFF5A:
            ch = chr(o - 0xFEE0)
        out.append({'－': '-', '＆': '&', '．': '.'}.get(ch, ch))
    return re.sub(r'\s+', ' ', ''.join(out)).strip()


def expected(info, today, now):
    """ページ → 期待する枠の集合（名前の頭・試合日・開始・発売・締切・売り切れ）と読めない受付の数"""
    day = info['day']
    groups = {}
    for nm, st, en, icon in info['wins']:
        groups.setdefault((nm, st, en), []).append(icon)
    out, unknown = [], 0
    for (nm, st, en), icons in groups.items():
        if en is not None and en < now:
            continue
        if en is None or en.date().isoformat() > day:
            end_date, end_txt = day, '%d/%d' % (int(day[5:7]), int(day[8:10]))
        else:
            end_date, end_txt = en.date().isoformat(), '%d/%d %d:%02d' % (en.month, en.day, en.hour, en.minute)
        sale = start_date = None
        sold = False
        if st > now:
            sale, start_date = '%d/%d %d:%02d' % (st.month, st.day, st.hour, st.minute), st.date().isoformat()
        elif 1 in icons or 2 in icons:
            pass
        elif icons and set(icons) == {3}:
            sold = True
        else:
            unknown += 1
            continue
        out.append((norm_name(nm), sale, end_txt, sold, end_date, start_date))
    return out, unknown


BADGE_RE = re.compile(r'^(?P<name>.*)（(?:(?P<pref>(?!R\d+年)[^\s（）]+) )?(?:R(?P<r>\d+)年 )?(?P<show>\d{1,2}/\d{1,2})'
                      r'(?: (?P<time>\d{1,2}:\d{2}))?公演）(?:(?P<sale>\d{1,2}/\d{1,2} \d{1,2}:\d{2})発売)?'
                      r'〜(?P<end>\d{1,2}/\d{1,2}(?: \d{1,2}:\d{2})?)$')


def check_entry(e, html, today, now):
    ng = []
    info = page_info(html)
    day = info['day']
    if not day:
        raise ValueError('試合日が読めない')
    ty = int(today[:4])
    show = '%s%d/%d' % ('R%d年 ' % (int(day[:4]) - 2018) if int(day[:4]) > ty else '', int(day[5:7]), int(day[8:10]))
    reg = []
    for t in e.get('tickets') or []:
        if 'ticketrugby.jp' not in (t.get('url') or ''):
            continue
        m = BADGE_RE.match(t.get('type') or '')
        if not m:
            ng.append('バッジの文字が読めない: %s' % t.get('type'))
            continue
        bshow = ('R%s年 ' % m.group('r') if m.group('r') else '') + m.group('show')
        if bshow != show or (m.group('time') or None) != info['time']:
            ng.append('バッジの試合日・開始が違う: %s（ページ %s %s）' % (t['type'], show, info['time']))
        if (m.group('pref') or '') != (e.get('prefecture') or ''):
            ng.append('バッジの県「%s」≠ カードの県「%s」' % (m.group('pref'), e.get('prefecture')))
        reg.append((m.group('name'), m.group('sale'), m.group('end'), bool(t.get('soldout')), t.get('date'),
                    t.get('startDate') if m.group('sale') else None))
    exp, unknown = expected(info, today, now)
    # 受付名は28字で切ることがある＝登録の名前がページの名前の頭と一致すればよい（切り口のカッコは整える）
    left = list(exp)
    for r in reg:
        hit = next((x for x in left if (x[0] == r[0] or (len(r[0]) >= 20 and x[0].startswith(r[0])))
                    and x[1:] == r[1:]), None)
        if hit:
            left.remove(hit)
            # 28字で切ると同じ文字になる受付（「…先行発売」と「…先行発売＜車椅子席＞」）は画面で1つのバッジ＝まとめて消し込む
            if len(r[0]) >= 20:
                left = [x for x in left if not (x[0].startswith(r[0]) and x[1:] == r[1:])]
        else:
            ng.append('登録にだけある: %s' % (r,))
    for x in left:
        ng.append('ページにだけある: %s' % (x,))
    if e.get('date') != day:
        ng.append('カードの日付 %s ≠ 試合日 %s' % (e.get('date'), day))
    if info['venue'] and info['venue'] != e.get('venue'):
        ng.append('会場が違う: 登録「%s」／ページ「%s」' % (e.get('venue'), info['venue']))
    p = info['pref']
    p2 = p if p == '北海道' else p[:-1] if p[-1:] in '都府県' else p
    if p2 != (e.get('prefecture') or ''):
        ng.append('県が違う: 登録「%s」／ページ「%s」' % (e.get('prefecture'), p))
    if info['venue'] and not (e.get('name') or '').endswith('（%s）' % info['venue']):
        ng.append('カード名の後ろに会場が無い: %s' % e.get('name'))
    return ng, unknown


def _selftest():
    now = datetime.datetime(2026, 11, 20, 12, 0)
    page = ('<main><h2>チケット発売情報</h2><span class="year">2026.</span><span class="date">11.21</span><span>土</span>'
            '<span>開場</span><span>11:00</span><span>開始</span><span>13:00</span>'
            '<p>トヨタスポーツセンター　陸上競技場（愛知県）</p><span>その他</span><p>A対B</p>'
            '<ul class="game_sec_r_infoli"><li><img src="/img/event/ico_st1.png"><p>空席あり</p></li></ul>'
            '<div><img src="/img/event/ico_st3.png"><p>指定席</p><p>4,000円</p></div>'
            '<div><img src="/img/event/ico_st4_d.png"><p>【トヨタV】一次先行発売 4,000円</p></div>'
            '<table><tr><th>販売期間</th><td>2026/10/10(土) 10:00～2026/10/17(土) 9:59</td></tr></table>'
            '<div><img src="/img/event/ico_st3_d.png"><p>一般発売 4,000円</p></div>'
            '<table><tr><th>販売期間</th><td>2026/10/17(土) 10:00～2026/11/21(土) 14:00</td></tr></table>'
            '<div><img src="/img/event/ico_st1.png"><p>自由席</p><p>1,000円～2,000円</p></div>'
            '<div><img src="/img/event/ico_st1_d.png"><p>一般発売 1,000円～2,000円</p></div>'
            '<table><tr><th>販売期間</th><td>2026/10/17(土) 10:00～2026/11/21(土) 14:00</td></tr></table>'
            '<div><img src="/img/event/ico_st4_d.png"><p>二次 抽選(FC)/先行 1,000円</p></div>'
            '<table><tr><th>販売期間</th><td>2026/12/01(火) 10:00～2026/12/05(土) 23:59</td></tr></table></main>')
    good = {'name': 'A対B（トヨタスポーツセンター 陸上競技場）', 'date': '2026-11-21', 'venue': 'トヨタスポーツセンター 陸上競技場',
            'prefecture': '愛知', 'tickets': [
                {'type': '一般発売（愛知 11/21 13:00公演）〜11/21 14:00', 'date': '2026-11-21', 'url': 'https://ticketrugby.jp/ticket_release_info/1'},
                {'type': '二次 抽選（FC）/先行（愛知 11/21 13:00公演）12/1 10:00発売〜11/21', 'date': '2026-11-21', 'startDate': '2026-12-01',
                 'url': 'https://ticketrugby.jp/ticket_release_info/1'}]}
    ng, unk = check_entry(good, page, '2026-11-20', now)
    assert ng == [] and unk == 0, ng
    bad = json.loads(json.dumps(good))
    bad['tickets'][0]['soldout'] = True
    assert check_entry(bad, page, '2026-11-20', now)[0]
    for k, v in (('date', '2026-11-22'), ('venue', 'X'), ('prefecture', '東京')):
        assert check_entry(dict(good, **{k: v}), page, '2026-11-20', now)[0], k
    assert check_entry(dict(good, tickets=good['tickets'][:1]), page, '2026-11-20', now)[0]
    bad = json.loads(json.dumps(good))
    bad['tickets'][0]['type'] = '一般発売（愛知 11/21 13:00公演）〜11/21 13:00'
    assert check_entry(bad, page, '2026-11-20', now)[0]
    pi = page_info('<h2>チケット発売情報</h2><span>2026.</span><span>12.20</span><span>日</span><span>開始</span><span>14:30</span>'
                   '<p>ヤマハスタジアム（磐田）（静岡県）</p>')
    assert (pi['venue'], pi['pref'], pi['time']) == ('ヤマハスタジアム（磐田）', '静岡県', '14:30'), pi
    print('selftest OK: 会場名の中のカッコ/文字の並びから別の読み方で枠を作る/売り切れ・締切・発売日・枠の不足・日付・会場・県で鳴る')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ids', default='')
    ap.add_argument('--built', default='')
    ap.add_argument('--today', default=(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)).date().isoformat())
    ap.add_argument('--sleep', type=float, default=3.0)
    ap.add_argument('--report', default=REPORT)
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        _selftest()
        sys.exit(0)
    if a.built:
        ents = json.load(io.open(a.built, encoding='utf-8'))['entries']
        targets = [(e, i) for i, e in enumerate(ents)]
    else:
        h = io.open('index.html', encoding='utf-8', newline='').read()
        ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
        want = {int(x) for x in re.findall(r'\d+', a.ids)} if a.ids else None
        targets = [(e, e['id']) for e in ev if 'ticketrugby.jp/' in json.dumps(e.get('links') or {}) + json.dumps(e.get('tickets') or [])
                   and (not want or e['id'] in want)]
    ok, ng, err, unk_all = 0, [], [], []
    for e, key in targets:
        urls = sorted({u for t in (e.get('tickets') or []) + [{'url': (e.get('links') or {}).get('ticketrugby')}]
                       for u in URL_RE.findall(t.get('url') or '')})
        if len(urls) != 1:
            ng.append((e, key, ['発売情報のページが %d 個（1試合1カードのはず）: %s' % (len(urls), urls)]))
            continue
        try:
            html = get('https://ticketrugby.jp/ticket_release_info/%s' % urls[0], a.sleep)
            now = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)).replace(tzinfo=None)
            msgs, unk = check_entry(e, html, a.today, now)
        except RuntimeError as ex:
            err.append((e, key, urls[0], str(ex)))
            break
        except Exception as ex:
            err.append((e, key, urls[0], str(ex)[:80]))
            continue
        if unk:
            unk_all.append((e, key, unk))
        if msgs:
            ng.append((e, key, msgs))
        else:
            ok += 1
    rep = io.open(a.report, 'w', encoding='utf-8')
    rep.write('=== gate_rugby_slots (today=%s) %s 対象%d件 ===\n' % (a.today, a.built or 'index.html', len(targets)))
    for e, key, msgs in ng:
        rep.write('\n🚨 id=%s %s\n    %s\n' % (key, (e.get('name') or '')[:50], (e.get('links') or {}).get('ticketrugby')))
        for m in msgs:
            rep.write('    %s\n' % m)
    for e, key, unk in unk_all:
        rep.write('\nℹ️ 期間の中なのに印が読めない受付 %d（組み立ては載せていない） id=%s %s\n' % (unk, key, (e.get('name') or '')[:40]))
    for e, key, u, why in err:
        rep.write('❌ id=%s release/%s 読めなかった: %s\n' % (key, u, why))
    rep.write('\n=== 集計: 一致 %d / 🚨食い違い %d / ❌読めなかった %d / ℹ️読めない印があるカード %d ===\n'
              % (ok, len(ng), len(err), len(unk_all)))
    rep.close()
    sys.stderr.write('gate_rugby_slots: match=%d ng=%d fetcherr=%d unknown=%d -> %s\n' % (ok, len(ng), len(err), len(unk_all), a.report))
    sys.exit(2 if (ng or err) else 0)


if __name__ == '__main__':
    main()
