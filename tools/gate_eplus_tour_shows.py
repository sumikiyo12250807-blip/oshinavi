# -*- coding: utf-8 -*-
"""【e+ 登録済みカードの「公演の抜け」番人】同じ e+ の催し（detail の10桁が同じ）の公演が、カードに全部入っているか。

🚨 なぜ作ったか（2026-11-13 抜き打ち・すちこ「ゲートを改善してる？」）
  44172 きいやま商店＝e+ の同じページ 0704830001 に5公演（11/20 名古屋・11/29 北海道・12/13 大阪・12/25 福岡・1/15 東京）
  あるのに、カードは福岡・東京の2公演だけ。抜けた3公演は「予定枚数終了」＝売り切れでも公演がこれからなら載せる決まり。
  reconcile_eplus は**カードに登録済みの公演ページしか開かない**＝登録に無い公演は永久に見えなかった。
  gate_eplus_slots の B（公演の取りこぼし）は投入の時だけ・しかも「買える枠が無い公演は指摘しない」。

見るもの＝カードの e+ の URL から出演者ページ（/sf/word/）の id を取り、e+ の公演API（eplus_word_koen.koen_by_word）で全公演を引く。
  そのうち detail の10桁がカードと同じ・公演日が今日以降・カードの URL に無い・カードの券種名に「M/D公演」が無い公演を出す。
  状態（受付中／受付前／予定枚数終了など）も添える＝受付中は足す・売り切れは売り切れの枠で足す。

使い方:
  python tools/gate_eplus_tour_shows.py --ids 44172,4236
  python tools/gate_eplus_tour_shows.py --third      # 登録済みを3日で一周（reconcile_eplus と同じ組）
  python tools/gate_eplus_tour_shows.py --new
報告＝tmp/gate_eplus_tour_report.txt（「🚨 id=…」の行）。終了コード 0=抜けなし / 1=抜けあり / 2=読めないものあり
🚨 e+ を叩くほかの道具（reconcile_eplus・eplus_harvest など）と同時に回さない（503）。
"""
import argparse, datetime, io, json, re, sys, time, importlib.util
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
TODAY = datetime.date.today()
REPORT = 'tmp/gate_eplus_tour_report.txt'


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    argv = sys.argv
    sys.argv = [path, '__gate__']
    try:
        sp.loader.exec_module(m)
    except SystemExit:
        pass
    finally:
        sys.argv = argv
    return m


def eid_of(u):
    m = re.search(r'eplus\.jp/sf/detail/(\d{10})', u or '')
    return m.group(1) if m else None


def strip_q(u):
    return re.sub(r'\?.*$', '', u or '')


def to_date(s):
    s = re.sub(r'\D', '', str(s or ''))[:8]
    try:
        return datetime.date(int(s[:4]), int(s[4:6]), int(s[6:8]))
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ids', default='')
    ap.add_argument('--new', action='store_true')
    ap.add_argument('--third', action='store_true')
    ap.add_argument('--sleep', type=float, default=1.0)
    a = ap.parse_args()
    eh = _load('eh', 'tools/eplus_harvest.py')
    ewk = _load('ewk', 'tools/eplus_word_koen.py')
    h = io.open('index.html', encoding='utf-8').read()
    E = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);', h, re.S).group(1))

    def eurls(e):
        us = [strip_q(t.get('url')) for t in e.get('tickets') or [] if 'eplus.jp/sf/detail/' in (t.get('url') or '')]
        le = strip_q((e.get('links') or {}).get('eplus'))
        if 'eplus.jp/sf/detail/' in le:
            us.append(le)
        return list(dict.fromkeys(us))

    targ = [e for e in E if eurls(e)]
    if a.ids:
        want = {int(x) for x in re.findall(r'\d+', a.ids)}
        targ = [e for e in targ if e['id'] in want]
    elif a.new:
        targ = [e for e in targ if e.get('genre') == 'new']
    elif a.third:
        grp = TODAY.toordinal() % 3
        targ = [e for e in targ if e['id'] % 3 == grp]
    else:
        print('対象を指定して: --ids / --new / --third'); return 2

    # 🚨同じ e+ の催しを OSHINAVI では別カードに分けて載せることがある（スカパラ＝ホールツアー 4236・武道館 22944・福岡 22945）
    #   ＝カード1枚でなく、同じ10桁を持つ全カードの URL と「M/D公演」で見る（初回の試しで 4236・22944 を抜けと誤って出した）
    ALL_U, ALL_T = set(), {}
    for x in E:
        xs = eurls(x)
        ALL_U.update(xs)
        tx = ' '.join(t.get('type') or '' for t in x.get('tickets') or [])
        for d10 in {eid_of(u) for u in xs} - {None}:
            ALL_T[d10] = ALL_T.get(d10, '') + ' ' + tx
    #   さらに同じ出演者のカード（ぴあで作った分も）の券種名を見る（2回目の試しで スカパラ 大阪城ホール＝24309・
    #   スタレビ 四国＝24307「香川・愛媛・高知 R9年 2/11〜2/14公演」が別カードにあった）
    def norm(s):
        return re.sub(r'[\s　・☆★!！]', '', s or '')
    ART = {}
    for x in E:
        tx = ' '.join(t.get('type') or '' for t in x.get('tickets') or [])
        ART[norm(x.get('artist'))] = ART.get(norm(x.get('artist')), '') + ' ' + tx

    def covered(md_t, txt):
        m_, d_ = md_t
        if re.search(r'(?<![\d/])%d/%d(?:\s*\d{1,2}:\d{2})?公演' % (m_, d_), txt):
            return True
        for a1, b1, a2, b2 in re.findall(r'(?<![\d/])(\d{1,2})/(\d{1,2})〜(?:R\d+年\s*)?(\d{1,2})/(\d{1,2})公演', txt):
            lo, hi = (int(a1), int(b1)), (int(a2), int(b2))
            if lo <= hi and lo <= (m_, d_) <= hi:
                return True
            if lo > hi and ((m_, d_) >= lo or (m_, d_) <= hi):   # 年をまたぐ範囲
                return True
        return False
    page_cache, word_cache = {}, {}
    hits, unread = [], []
    for e in targ:
        us = eurls(e)
        eids = {eid_of(u) for u in us} - {None}
        have_u = set(us)
        types = ' '.join(t.get('type') or '' for t in e.get('tickets') or [])
        wid = None
        for u in us:
            if u not in page_cache:
                try:
                    page_cache[u] = eh.fetch(u)
                except Exception as ex:
                    page_cache[u] = ''
                time.sleep(a.sleep)
            m = re.search(r'/sf/word/(\d+)', page_cache[u] or '')
            if m:
                wid = m.group(1); break
        if not wid:
            unread.append((e['id'], e.get('name'), '出演者ページの id が取れない'))
            continue
        if wid not in word_cache:
            try:
                word_cache[wid] = [ewk.simp(r) for r in ewk.koen_by_word(wid, sleep=a.sleep)]
            except Exception as ex:
                word_cache[wid] = None
        recs = word_cache[wid]
        if recs is None:
            unread.append((e['id'], e.get('name'), '公演APIが読めない word=%s' % wid))
            continue
        miss = []
        for r in recs:
            u = r.get('url') or ''
            if u.startswith('/'):
                u = 'https://eplus.jp' + u
            u = strip_q(u)
            if eid_of(u) not in eids or u in have_u or u in ALL_U:
                continue
            d = to_date(r.get('date'))
            if not d or d < TODAY:
                continue
            if covered((d.month, d.day), types + ' ' + ALL_T.get(eid_of(u), '') + ' ' + ART.get(norm(e.get('artist')), '')):
                continue
            # 🚨（試し3回目 11/13）受付が終わっただけの公演（パンダドラゴン 大阪11/14・GUMMY 12/12〜13）は載せない＝出さない。
            #   出すのは 買える受付（受付中・受付前）がある公演 と 予定枚数終了（売り切れ＝公演がこれからなら載せる）の公演だけ
            if u not in page_cache:
                try:
                    page_cache[u] = eh.fetch(u)
                except Exception:
                    page_cache[u] = ''
                time.sleep(a.sleep)
            sh = page_cache[u]
            if not sh:
                unread.append((e['id'], e.get('name'), '公演ページが読めない ' + u))
                continue
            live = [w for w in eh.parse_windows(sh) if w['status'] != 'ended' and w['ed'] >= TODAY]
            sold = bool(re.search(r'ticket-status__item[^"]*">[^<]*予定枚数終了', sh))
            if not live and not sold:
                continue
            miss.append((d.isoformat(), r.get('pref') or '', r.get('venue') or '', '受付あり' if live else '予定枚数終了', u))
        if miss:
            hits.append((e, miss))
    L = ['=== gate_eplus_tour_shows (today=%s) 対象%d件 ===' % (TODAY, len(targ)),
         '公演の抜け %d件 / 読めない %d件' % (len(hits), len(unread)), '']
    for e, miss in hits:
        L.append('🚨 id=%s %s ＋%d公演' % (e['id'], (e.get('name') or '')[:40], len(miss)))
        for d, p, v, s, u in sorted(miss):
            L.append('    %s %s %s %s  %s' % (d, p, v[:30], s, u))
    for i, n, why in unread:
        L.append('⚠️ id=%s %s 読めない：%s' % (i, (n or '')[:40], why))
    io.open(REPORT, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print('\n'.join(L[:2]))
    print('→', REPORT)
    return 1 if hits else (2 if unread else 0)


if __name__ == '__main__':
    sys.exit(main())
