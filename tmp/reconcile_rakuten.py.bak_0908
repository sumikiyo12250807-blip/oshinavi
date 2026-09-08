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
    args = ap.parse_args()

    h = open('index.html', encoding='utf-8').read()
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
    EV = json.loads(m.group(2))
    ids = {int(x) for x in args.ids.split(',') if x.strip()}
    targets = [e for e in EV
               if (e.get('links') or {}).get('rakuten')
               and (e['id'] in ids if ids else (e.get('genre') == 'new' if args.new else True))]

    print('=== reconcile_rakuten (today=%s) 対象%d件 ===\n' % (TODAY, len(targets)))
    ok = fail = fetcherr = unparsable = 0
    skip_slots = checked_slots = 0
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
            perfs += R.parse_perfs(b)
            wins += R.parse_windows(b)
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

        errs = []
        for t in e.get('tickets', []):
            checked = False
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
                else:
                    errs.append('締切 %s がページに無い | %s' % (t['date'], t['type'][:34]))
            # ② 発売日
            if t.get('startDate'):
                if t['startDate'] in page_start:
                    checked = True
                else:
                    errs.append('発売日 %s がページに無い | %s' % (t['startDate'], t['type'][:34]))
            # ③ バッジの公演日
            for md in re.findall(r'(\d{1,2}/\d{1,2})公演', t['type']) or []:
                pass
            badge = re.search(r'（[^）]*?([\d/〜]+)公演）', t['type'])
            if badge:
                for one in badge.group(1).split('〜'):
                    if one and one not in page_perf_md:
                        errs.append('バッジ公演日 %s がページに無い | %s' % (one, t['type'][:34]))
                    else:
                        checked = True
            checked_slots += 1 if checked else 0
            skip_slots += 0 if checked else 1
        # ④ 県。複数会場のエントリは prefecture が「大阪・東京」のように多県を名乗る（正しい表記）。
        #   丸ごと1県として比較すると必ず外れるので、**分解して全部がページ側に在るか**で見る
        #   （ぴあ側の「統合バッジが多県名乗るのは正」と同じ扱い＝[[reference_reconcile_pia_qc_gate]]）。
        #   2026-07-30: id5 Rol3ert（大阪・東京の2会場）が誤検知でFAILしていた。
        if e.get('prefecture') and e['prefecture'] != '全国' and page_pref:
            mine = [p for p in re.split(r'[・/／]', e['prefecture']) if p]
            miss = [p for p in mine if p not in page_pref]
            if miss:
                errs.append('県 %s がページ(%s)に無い' % ('・'.join(miss), '/'.join(sorted(page_pref))))

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
        print('   ※未照合＝締切が「公演日で締めた/売り切れ次第終了」で突合対象が無い枠。正しいと確認できていない。')
    return 1 if (fail or fetcherr) else 0


if __name__ == '__main__':
    sys.exit(main())
