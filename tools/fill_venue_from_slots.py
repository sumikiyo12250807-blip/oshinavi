# -*- coding: utf-8 -*-
"""県が2つ以上なのに会場が1つのカード（gate_fields の O）に、受付の売り場ページから会場を足す（2026-11-17 新設）。

きっかけ＝11/17 TikTok 説明文の独立FCで 27277 早見優・松本伊代・森口博子「青春のアイドルヒットステージ」＝
  受付は 秋田 2/27（あきた芸術劇場ミルハス）と 福岡 3/18 の2つ・県は「福岡・秋田」なのに、会場は「福岡市民ホール 大ホール」だけ・
  会期の表示も「… 福岡 福岡市民ホール 大ホール」。ヒール（heal_stale_deadlines）は後から足された会場の受付を tickets と県には足すが、
  venue と dateLabel は誰も直さない。gate_fields の O は 11/2 から「既存は件数だけ」で 121件たまっていた
  （11/2 rootcause C で「会場を足す道具を作る」と決めて作っていなかった）。

やること：まだ出ている受付の url（ぴあ eventCd・e+ detail）を開いて会場と公演日を読み、公演日の順に並べて
  venue＝「全国ツアー（会場1／会場2…）」・dateLabel の後ろ＝組み立てと同じ（県が4つまでは県を並べる・5つ以上は「全国ツアー」）。
  開いた結果、会場が本当に1つ（県だけ2つ）なら触らず tools/venue_ok.json に控える（番人で鳴らさない）。
使い方:
  python tools/fill_venue_from_slots.py                 … 下見（O の既存全部・ぴあ/e+ の受付があるものだけ）
  python tools/fill_venue_from_slots.py --ids 27277     … 指定だけ
  python tools/fill_venue_from_slots.py --apply --lock tmp/x1112/index.lock
"""
import datetime, html, io, json, os, re, sys, time
ROOT = 'C:/Users/user/oshinavi/'
sys.path.insert(0, ROOT + 'tools')
import compact_events as C  # noqa: E402

TODAY = datetime.date.today().isoformat()
OKF = ROOT + 'tools/venue_ok.json'


def is_O(e):
    return ((e.get('date') or '') >= TODAY and '・' in (e.get('prefecture') or '')
            and '／' not in (e.get('venue') or '') and not (e.get('venue') or '').startswith('全国ツアー'))


def live_urls(e):
    out = []
    for t in e.get('tickets') or []:
        if not ((t.get('date') or '') >= TODAY or t.get('soldout') or t.get('saleUntilSoldOut')):
            continue
        u = t.get('url') or ''
        if ('pia.jp' in u and 'eventCd=' in u) or re.search(r'eplus\.jp/sf/detail/\d+-P\d+', u):
            if u not in out:
                out.append(u)
    return out


def pia_venue(u):
    import build_pia_entries as B
    h = B.fetch(u)
    h = re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>', ' ', h)
    t = html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', h)))
    # 展覧会のページは「会期」「開催期間」・会場の括弧の後ろに説明が続く（3410 キボリノコンノ展・5487 河鍋暁斎）
    m = re.search(r'(?:公演期間|会期|開催期間|期間)\s*(\d{4})/(\d{1,2})/(\d{1,2})\S*.*?会場\s*(.+?)\s*[(（]\s*([^()（）]+?[都道府県])\s*[)）]', t)
    if not m:
        return None
    return ('%s-%02d-%02d' % (m.group(1), int(m.group(2)), int(m.group(3))), B.norm_fw(m.group(4)).strip())


def ep_venue(u):
    from eplus_harvest import fetch, parse_ld
    ld = parse_ld(fetch(u))
    if not ld:
        return None
    ld.sort(key=lambda x: x['date'])
    return (ld[0]['date'], ld[0]['venue'])


def tail_for(pref, venues):
    n = len([p for p in (pref or '').split('・') if p])
    if n >= 5 or pref == '全国':
        return '全国ツアー'
    return pref if len(venues) > 1 else (pref + ' ' + venues[0]).strip()


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    apply = '--apply' in sys.argv
    E = C.load(io.open(ROOT + 'index.html', encoding='utf-8', newline='').read())
    try:
        OK = set(json.load(io.open(OKF, encoding='utf-8')))
    except FileNotFoundError:
        OK = set()
    if '--ids' in sys.argv:
        ids = {int(x) for x in sys.argv[sys.argv.index('--ids') + 1].split(',')}
        tg = [e for e in E if e['id'] in ids]
    else:
        tg = [e for e in E if e.get('genre') != 'new' and is_O(e) and str(e['id']) not in OK]
    fix, single, cannot = {}, [], []
    for e in tg:
        us = live_urls(e)
        if not us:
            cannot.append(e)
            continue
        got = []
        for u in us:
            try:
                r = pia_venue(u) if 'pia.jp' in u else ep_venue(u)
            except Exception:
                r = None
            time.sleep(1.0)
            if r and r[1]:
                got.append(r)
        if not got:
            cannot.append(e)
            continue
        got.sort()
        vs = []
        for _, v in got:
            if v not in vs:
                vs.append(v)
        if len(vs) <= 1:
            single.append(e)
            print(f"id{e['id']} 会場は1つ（{vs[0] if vs else ''}）＝そのまま・venue_ok に控える")
            continue
        nv = '全国ツアー（' + '／'.join(vs) + '）'
        dl = e.get('dateLabel') or ''
        m = re.match(r'(\d{4}年\d{1,2}月\d{1,2}日\([^)]\)(?:〜\d{4}年\d{1,2}月\d{1,2}日\([^)]\))?)(\s|$)', dl)
        ndl = (m.group(1) + ' ' + tail_for(e.get('prefecture'), vs)) if m else dl
        fix[e['id']] = (nv, ndl)
        print(f"id{e['id']} {(e.get('name') or '')[:24]}｜会場 {(e.get('venue') or '')[:24]} → {nv[:70]}｜会期 {dl[:40]} → {ndl[:40]}")
    print(f'fill_venue_from_slots: 直す {len(fix)} / 会場は本当に1つ {len(single)} / ぴあ・e+ の受付が無く読めない {len(cannot)}'
          + (' ' + ','.join(str(e['id']) for e in cannot[:40]) if cannot else ''))
    if not apply:
        return
    lock = sys.argv[sys.argv.index('--lock') + 1] if '--lock' in sys.argv else None
    while lock:
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'fill_venue'); os.close(fd); break
        except FileExistsError:
            time.sleep(5)
    try:
        # 書く直前に読み直して、会場と会期の欄だけ id で差し替える（読んでいる間にほかの道具が書いた分を消さない）
        text = io.open(ROOT + 'index.html', encoding='utf-8', newline='').read()
        E2 = C.load(text)
        n = 0
        for e in E2:
            if e['id'] in fix:
                e['venue'], e['dateLabel'] = fix[e['id']]
                n += 1
        s, end, _ = C.locate(text)
        io.open(ROOT + 'index.html', 'w', encoding='utf-8', newline='').write(text[:s] + C.dump(E2, True, '\r\n') + text[end:])
        OK |= {str(e['id']) for e in single}
        json.dump(sorted(OK, key=int), io.open(OKF, 'w', encoding='utf-8'), indent=0)
        print(f'書いた {n}件・venue_ok {len(OK)}件')
    finally:
        if lock and os.path.exists(lock):
            os.remove(lock)


if __name__ == '__main__':
    main()
