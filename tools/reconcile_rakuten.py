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
    ok = fail = fetcherr = 0
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
        # ④ 県
        if e.get('prefecture') and e['prefecture'] != '全国' and page_pref and e['prefecture'] not in page_pref:
            errs.append('県 %s がページ(%s)と違う' % (e['prefecture'], '/'.join(sorted(page_pref))))

        if errs:
            fail += 1
            print('🚨 id=%s %s' % (e['id'], e['name'][:40]))
            for x in dict.fromkeys(errs):
                print('    %s' % x)
        else:
            ok += 1
            print('✅ id=%s %s | 一致' % (e['id'], e['name'][:40]))

    print('\n=== 集計: OK %d / 🚨FAIL %d / ❌FETCH %d ===' % (ok, fail, fetcherr))
    print('=== QC照合カバレッジ: 照合できた枠 %d / 未照合 %d ===' % (checked_slots, skip_slots))
    if skip_slots:
        print('   ※未照合＝締切が「公演日で締めた/売り切れ次第終了」で突合対象が無い枠。正しいと確認できていない。')
    return 1 if (fail or fetcherr) else 0


if __name__ == '__main__':
    sys.exit(main())
