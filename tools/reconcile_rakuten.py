# -*- coding: utf-8 -*-
"""楽天用QCゲート＝登録した表示値が楽天の実ページと一致するかを独立照合する。

  python tools/reconcile_rakuten.py --new      # genre:"new" の楽天エントリだけ
  python tools/reconcile_rakuten.py --ids 3218,3219

ぴあの reconcile_pia / e+ の reconcile_eplus と同じ役割（[[reference_reconcile_pia_qc_gate]]）。
**ビルダーの出力と突き合わせるのではなく、実ページの生の値と突き合わせる**＝同じバグで両方間違える
のを避ける。照合するのは画面に出る値だけ:
   ① バッジの締切(ticket.date)     … ページの販売終了日時(カードのmax_end_on / 販売枠のtimming終端)にあるか
   ② バッジの発売日(ticket.startDate) … ページの販売開始日時にあるか
   ③ バッジの公演日(（… M/D公演）)  … ページの公演日にあるか
   ④ 都道府県                      … ページのエリアと一致するか
一致を確認できなかった枠は **skip(未照合)** として必ず件数を出す（QC 0＝全部正しい、ではない）。
"""
import argparse
import datetime
import json
import re
import sys

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_harvest as R

TODAY = datetime.date.today().isoformat()


def md_set(dates):
    out = set()
    for d in dates:
        if d:
            out.add('%d/%d' % (int(d[5:7]), int(d[8:10])))
    return out


RAKUTEN_URL = re.compile(r'ticket\.rakuten\.co\.jp|linksynergy\.com/deeplink')


def rakuten_slot(e, t):
    """この枠を楽天のページと突き合わせてよいか。

    🚨楽天リンクを持つエントリでも、枠そのものはぴあ/e+のことがある（買うボタンだけ楽天）。
      それを楽天のページと照合すると必ず外れる＝本物のFAILが埋もれる。
      url が楽天なら見る。url が空の枠は、そのエントリに**他社リンクが1つも無い時だけ**見る。
    """
    u = t.get('url') or ''
    if u:
        return bool(RAKUTEN_URL.search(u))
    ls = e.get('links') or {}
    return not any(ls.get(k) for k in ('pia', 'eplus', 'lawson'))


def past(d):
    """今日より前＝楽天のページからは消えている。照合できないだけで、登録が誤りとは限らない。"""
    return bool(d) and d[:10] < TODAY


def raw_url(u):
    m = re.search(r'murl=([^&]+)', u or '')
    if m:
        import urllib.parse
        return urllib.parse.unquote(m.group(1))
    return u


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--new', action='store_true')
    ap.add_argument('--ids', default='')
    # 直す前のバックアップに当てて「本当に鳴るか」を確かめるための入口（陰性テスト用）
    ap.add_argument('--index', default='index.html')
    args = ap.parse_args()

    h = open(args.index, encoding='utf-8').read()
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
    EV = json.loads(m.group(2))
    ids = {int(x) for x in args.ids.split(',') if x.strip()}
    targets = [e for e in EV
               if (e.get('links') or {}).get('rakuten')
               and (e['id'] in ids if ids else (e.get('genre') == 'new' if args.new else True))]

    print('=== reconcile_rakuten (today=%s) 対象%d件 ===\n' % (TODAY, len(targets)))
    ok = fail = fetcherr = unparsable = 0
    skip_slots = checked_slots = 0
    skipped = []          # 🚨未照合の**中身**を出す（数だけだと死角が見えない）
    for e in targets:
        # 統合エントリは枠ごとにURLが違う（ツアー/別券種）。**その枠のURL**を正として照合する。
        urls = [raw_url(e['links']['rakuten'])]
        for t in e.get('tickets', []):
            ru = raw_url(t.get('url') or '')
            if ru and ru not in urls:
                urls.append(ru)
        perfs, wins, bad = [], [], None
        for u in urls:
            try:
                b = R.fetch(u)
            except Exception as ex:
                bad = ex
                continue
            p1, w1 = R.parse_perfs(b), R.parse_windows(b)
            if not p1 and not w1:
                # 🆕新型＝HTMLは空の型だけで data-event-json が指す外部JSONに中身がある。
                #   ハーベスタ側と同じ条件で辿る（入口だけ読めて出口が読めないと照合が抜ける）。
                ej = R.parse_event_json(b)
                if ej:
                    p1, w1 = ej.get('perfs') or [], ej.get('windows') or []
            perfs += p1
            wins += w1
        if bad and not perfs:
            fetcherr += 1
            print('❌ id=%s %s | FETCH %s' % (e['id'], e['name'][:34], bad))
            continue
        # 楽天チケットmini(/mini/events/xxxx)は公演カードもsalesDisplayStatusも無い別レイアウト。
        # 取得できても中身がゼロ＝**照合できない**。ここを「ページに無い」と鳴らすと、正しい登録が
        # 毎回FAILに出て本物のFAILが埋もれる。黙って合格にもしない＝対象外として件数を必ず出す。
        # （2026-07-30: id6 古琴と琵琶の対話 が mini 形式で誤検知していた）
        if not perfs and not wins:
            unparsable += 1
            print('⏭️ id=%s %s | 照合対象外（公演カード/販売枠が取れないページ形式・要目視）'
                  % (e['id'], e['name'][:34]))
            for u in urls:
                print('      %s' % u)
            continue
        page_end = {p['sale_end'][:10] for p in perfs if p.get('sale_end')}
        page_start = {p['sale_start'][:10] for p in perfs if p.get('sale_start')}
        for w in wins:
            f, t = R.win_dates(w['timming'])
            if f:
                page_start.add(f[:10])
            if t:
                page_end.add(t[:10])
        page_perf_md = md_set([p['date'] for p in perfs] + [p.get('end') for p in perfs])
        page_pref = {re.sub(r'[都府県]$', '', p['pref']) for p in perfs if p['pref']}

        # 🚨🚨【2026-09-10 追加】「その締切は**その公演のもの**か」を見る。
        #   ①の照合は「登録の締切がページのどこかに在るか」しか見ないので、
        #   別の公演の締切を流用した嘘（＝ビルダーが max(カードの締切) を全公演に付けていた型）が
        #   **ページに実在する日付なので素通りする**。2026-09-10 朝、39件を照合して FAIL 0 だったのに
        #   実際は14エントリの締切が嘘だった（[[feedback_sale_end_unknown_display]]）。
        #   照合＝バッジが名乗る公演日のカードの締切、または販売枠(窓)の締切。そのどちらでもなければFAIL。
        #   🚨判定は「＝」でなく「その公演の締切より後を名乗っていないか」で見る。
        #     嘘はたいてい「複数公演を1枠にまとめた範囲バッジ」の形で出るので、
        #     単日バッジの等号照合だけでは1件も鳴らない（2026-09-10に実測して作り直した）。
        card_end_by_md, iso_by_md = {}, {}
        for p in perfs:
            for md in md_set([p['date']]):
                iso_by_md.setdefault(md, p['date'])
                if p.get('sale_end'):
                    card_end_by_md.setdefault(md, set()).add(p['sale_end'][:10])
        perf_end_iso = {}          # 公演のISO日 → その公演で最後まで買える日
        for p in perfs:
            if p.get('sale_end'):
                k = p['date']
                v = p['sale_end'][:10]
                if v > perf_end_iso.get(k, ''):
                    perf_end_iso[k] = v
        win_end = set()
        for w in wins:
            _f, _t = R.win_dates(w['timming'])
            if _t:
                win_end.add(_t[:10])

        errs = []
        for t in e.get('tickets', []):
            checked = False
            if not rakuten_slot(e, t):
                skip_slots += 1      # 🚨楽天の枠でない＝この道具の担当外（黙って合格にしない）
                skipped.append((e['id'], t.get('type', ''), '楽天の枠でない'))
                continue
            # ① 締切（公演日で締めた/売り切れ次第終了は照合対象外＝skip）
            if t.get('saleEndUnknown') or t.get('saleUntilSoldOut'):
                pass
            elif t['date'] in page_end or t['date'] in md_set([t['date']]) & set():
                checked = True
            elif t['date'] in {d for d in page_end}:
                checked = True
            else:
                # 公演日で締めた枠はページの公演日と一致していればOK
                if '%d/%d' % (int(t['date'][5:7]), int(t['date'][8:10])) in page_perf_md:
                    checked = True
                elif past(t['date']):
                    pass             # 🚨終わった枠はページから消える＝照合できないだけ
                else:
                    errs.append('締切 %s がページに無い | %s' % (t['date'], t['type'][:34]))
            # ② 発売日
            if t.get('startDate'):
                if t['startDate'] in page_start:
                    checked = True
                elif past(t['startDate']):
                    pass             # 🚨発売済みの先行はページの販売枠から落ちる
                else:
                    errs.append('発売日 %s がページに無い | %s' % (t['startDate'], t['type'][:34]))
            # ③ バッジの公演日
            #   🚨「（愛知 R9年 1/9 13:00公演）」の形（R9年＋開演時刻つき）がある。
            #     素朴に [\d/〜]+ で取ると時刻の「00」を拾って割れる（2026-09-10に落ちた）。
            #     M/D（と 〜M/D）だけを名指しで取り、R9年と開演時刻は落とす。
            _MD = r'(?:R\d+年\s*)?\d{1,2}/\d{1,2}'
            badge = re.search(r'（[^）]*?(%s(?:〜%s)?)(?:\s+\d{1,2}:\d{2})?公演）' % (_MD, _MD),
                              t['type'])
            if badge:
                for one in badge.group(1).split('〜'):
                    one = re.sub(r'^R\d+年\s*', '', one.strip())
                    if not one:
                        continue
                    if one in page_perf_md:
                        checked = True
                        continue
                    # 🚨ラベルは「事実の会期」を書く決まりなので、初日が過ぎたツアーは
                    #   ページ側だけが減る。これを鳴らすと毎回FAILになって本物が埋もれる。
                    mo, dy = (int(x) for x in one.split('/'))
                    yr = int(TODAY[:4]) + (1 if mo < int(TODAY[5:7]) - 6 else 0)
                    # 🚨当日分も鳴らさない＝楽天は「その日の公演の販売が閉じた時点」でカードを落とすので、
                    #   今日の公演はページに残っていないことがある（2026-09-09 id3244 来舞 来夢で実証）。
                    if '%04d-%02d-%02d' % (yr, mo, dy) <= TODAY:
                        continue
                    errs.append('バッジ公演日 %s がページに無い | %s' % (one, t['type'][:34]))
            # ③-2 その締切は「その枠が名乗っている公演」のものか
            #     ＝バッジが覆う公演のどれかで、締切がその公演のカードの締切より**後**なら嘘。
            #     販売枠(窓)に書かれた締切ならツアー全体に効くので、それは正しい。
            if (badge and not t.get('saleEndUnknown') and not t.get('saleUntilSoldOut')
                    and not past(t['date']) and t['date'] not in win_end and perf_end_iso):
                mds = [re.sub(r'^R\d+年\s*', '', x.strip()) for x in badge.group(1).split('〜')]
                lo = iso_by_md.get(mds[0]) or min(perf_end_iso)
                hi = iso_by_md.get(mds[-1]) or max(perf_end_iso)
                for pd in sorted(perf_end_iso):
                    if not (lo <= pd <= hi) or pd < TODAY:
                        continue     # 覆っていない公演／終わった公演は見ない
                    if t['date'] > perf_end_iso[pd]:
                        errs.append('締切 %s は %s公演のものでない（%s公演は %s まで／販売枠の締切は %s）| %s'
                                    % (t['date'], mds[0], pd, perf_end_iso[pd],
                                       '/'.join(sorted(win_end)) or '無し', t['type'][:34]))
                        break
            checked_slots += 1 if checked else 0
            skip_slots += 0 if checked else 1
            if not checked:
                why = ('締切が「公演日で締めた/売り切れ次第終了」で突合対象が無い'
                       if (t.get('saleEndUnknown') or t.get('saleUntilSoldOut'))
                       else ('終わった枠でページから消えている' if past(t.get('date'))
                             else '照合できる値が1つも無い'))
                skipped.append((e['id'], t.get('type', ''), why))
        # ④ 県。複数会場のエントリは prefecture が「大阪・東京」のように多県を名乗る（正しい表記）。
        #   丸ごと1県として比較すると必ず外れるので、**分解して全部がページ側に在るか**で見る
        #   （ぴあ側の「統合バッジが多県名乗るのは正」と同じ扱い＝[[reference_reconcile_pia_qc_gate]]）。
        #   2026-07-30: id5 Rol3ert（大阪・東京の2会場）が誤検知でFAILしていた。
        #   🚨2026-09-09: **他社の枠が混ざったエントリでは県を突き合わせない**。
        #   ツアー全体はぴあで押さえていて、楽天のページはその中の1都市分しか無いことがある
        #   （id1 さだまさし＝エントリは千葉・愛知を名乗り、楽天ページは東京11月公演だけ）。
        #   エントリ全体の県を1枚のページに求めると必ず外れる＝毎朝ノイズで鳴る。
        mixed = any(t.get('url') and 'rakuten' not in t['url'] and 'linksynergy' not in t['url']
                    for t in (e.get('tickets') or []))
        if e.get('prefecture') and e['prefecture'] != '全国' and page_pref and not mixed:
            mine = [p for p in re.split(r'[・/／]', e['prefecture']) if p]
            miss = [p for p in mine if p not in page_pref]
            if miss:
                errs.append('県 %s がページ(%s)に無い' % ('・'.join(miss), '/'.join(sorted(page_pref))))
        elif mixed:
            errs_note = '他社の枠が混ざるエントリなので県の突合はしない'
            if errs_note not in errs:
                pass   # 情報として出すほどではない（FAILにしない）

        if errs:
            fail += 1
            print('🚨 id=%s %s' % (e['id'], e['name'][:40]))
            for x in dict.fromkeys(errs):
                print('    %s' % x)
        else:
            ok += 1
            print('✅ id=%s %s | 一致' % (e['id'], e['name'][:40]))

    print('\n=== 集計: OK %d / 🚨FAIL %d / ❌FETCH %d / ⏭️照合対象外 %d ==='
          % (ok, fail, fetcherr, unparsable))
    if unparsable:
        print('   ※照合対象外＝ページ形式が違って一次情報が取れない分。「正しい」と確認できていない。')
    print('=== QC照合カバレッジ: 照合できた枠 %d / 未照合 %d ===' % (checked_slots, skip_slots))
    if skip_slots:
        print('   ※未照合＝「正しい」と確認できていない枠。QC 0＝全部正しい、ではない。')
        for i, ty, why in skipped:
            print('   ⏭️ id=%-5s %-52s … %s' % (i, ty[:52], why))
    return 1 if (fail or fetcherr) else 0


if __name__ == '__main__':
    sys.exit(main())
