# -*- coding: utf-8 -*-
"""ぴあのエントリの「会期（dateLabel・date）・会場（venue）・県（prefecture）」を、ぴあの今のページから**足すだけ**（消さない）。

  python tools/fill_entry_span.py --ids 5162,24203            … 下見（tmp/fill_entry_span.txt）
  python tools/fill_entry_span.py --ids 5162 --apply          … 書く（書く直前に index.html を読み直し、その欄だけ id で差し替える）
  python tools/fill_entry_span.py --gate [--limit 50]         … gate_fields の P／O に出た件（ぴあの link を持つ分）を対象に
  python tools/fill_entry_span.py --selftest

## なぜ要るか（2026-11-04 新設・tmp/x1104/spot/rootcause.md）
- 11/2 抜き打ち 24203 ブダペスト祝祭管（会場が横浜だけ）／11/4 抜き打ち 5162 山本彩（会期が「2/6 福岡」だけ・会場が4つ・県に東京なし）
- 登録のあとでぴあが会場・公演を足す（または足し込みの道具が枠だけ足す）と、**枠（tickets）はヒールで増えるが、
  会期・会場・県は誰も伸ばさない**（heal_stale_deadlines / heal_fany は「tickets だけ」の決まり＝手直しを巻き戻さないため）。
  県は fill_entry_pref が枠の括弧から足すが、会場名と会期は枠に書いていないので、ぴあのページを読まないと足せない。

## やること
build_pia_entries と同じ関数（parse_cards → span_rows）で「これから行われる全公演」の会場・県・初日・千秋楽を出し、
- venue：今の会場に無い会場だけ足す（2つ以上になったら「全国ツアー（A／B／…）」の形）
- prefecture：今の県に無い県だけ足す（組み立てと同じく 5県以上は「全国」）
- dateLabel：組み立ての書き方（YYYY年M月D日(曜)〜…）の時だけ、初日を前へ・千秋楽を後ろへ伸ばす。ほかの書き方は報告だけ
- date：千秋楽が今の date より後なら伸ばす
読めない（混雑・無効化）・枠が0のページは触らない。ぴあは1本ずつ（--sleep 既定 8秒）。
"""
import datetime, io, json, os, re, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_pia_entries as BP  # noqa: E402

ROOT = 'C:/Users/user/oshinavi/'
REPORT = ROOT + 'tmp/fill_entry_span.txt'
DL_RX = re.compile(r'^(\d{4})年(\d{1,2})月(\d{1,2})日\([^)]\)(?:〜(\d{4})年(\d{1,2})月(\d{1,2})日\([^)]\))?(\s.*)?$')
PREF_ENUM_MAX = 4


def load():
    text = io.open(ROOT + 'index.html', encoding='utf-8', newline='').read()
    m = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
    E, end = json.JSONDecoder().raw_decode(text, m.start(1))
    return text, m.start(1), end, E


def save(text, st, end, E):
    compact = text[st:st + 3].startswith('[\r\n{') or text[st:st + 3].startswith('[\n{')
    body = ('[\n' + ',\n'.join(json.dumps(x, ensure_ascii=False, separators=(',', ':')) for x in E) + '\n]') if compact \
        else json.dumps(E, ensure_ascii=False, indent=2)
    if '\r\n' in text[st:st + 3000]:
        body = body.replace('\r\n', '\n').replace('\n', '\r\n')
    io.open(ROOT + 'index.html', 'wb').write((text[:st] + body + text[end:]).encode('utf-8'))


def pia_urls(e):
    us = []
    for u in [(e.get('links') or {}).get('pia')] + [t.get('url') for t in e.get('tickets') or []]:
        if u and 'pia.jp' in u:
            n = BP.normalize_pia_url(u)
            if n not in us:
                us.append(n)
    return us


def span_of(htmls, today):
    """ページ群 → (venues, prefs, start, end)。枠が1つも無ければ None"""
    allrows = []
    for h in htmls:
        allrows += BP.parse_cards(h)
    if not allrows:
        return None
    span = BP.span_rows(allrows, [r for r in allrows if r['state'] in ('受付中', '発売前')], today)
    span = [r for r in span if r.get('perfdate')]
    if not span:
        return None
    venues = list(dict.fromkeys(BP.norm_fw(v) for r in span for v in (r.get('venues') or ([r['venue']] if r.get('venue') else []))))
    prefs = list(dict.fromkeys(p for r in span for p in r['prefs']))
    return venues, prefs, min(r['perfdate'] for r in span), max((r.get('perf_end') or r['perfdate']) for r in span)


def _vkey(v):
    return re.sub(r'[\s　]', '', BP.norm_fw(v or ''))


def plan(e, sp):
    """足す中身 {欄: (前, 後)}。足すものが無ければ {}"""
    venues, prefs, s0, s1 = sp
    out = {}
    # 会場
    v = e.get('venue') or ''
    mt = re.match(r'^全国ツアー（(.*)）$', v)
    have = [x for x in (mt.group(1).split('／') if mt else ([v] if v else [])) if x]
    hk = {_vkey(x) for x in have}
    add = [x for x in venues if _vkey(x) not in hk and not any(_vkey(x) in k or k in _vkey(x) for k in hk if k)]
    if add:
        allv = have + add
        out['venue'] = (v, allv[0] if len(allv) == 1 else '全国ツアー（' + '／'.join(allv) + '）')
    # 県
    p = (e.get('prefecture') or '').strip()
    if p not in ('全国', '海外'):
        hp = [x for x in p.split('・') if x]
        ap = [x for x in prefs if x not in hp]
        if ap:
            allp = hp + ap
            out['prefecture'] = (p, '全国' if len(allp) > PREF_ENUM_MAX else '・'.join(allp))
    # 会期
    dl = e.get('dateLabel') or ''
    m = DL_RX.match(dl)
    if m:
        lo = '%s-%02d-%02d' % (m.group(1), int(m.group(2)), int(m.group(3)))
        hi = ('%s-%02d-%02d' % (m.group(4), int(m.group(5)), int(m.group(6)))) if m.group(4) else lo
        nlo, nhi = min(lo, s0), max(hi, s1)
        if (nlo, nhi) != (lo, hi):
            pref = out.get('prefecture', (p, p))[1]
            vv = out.get('venue', (v, v))[1]
            if nlo == nhi:
                tail = f"{pref} {vv}".strip()
                ndl = f"{BP.jp(nlo)} {tail}".strip()
            else:
                tail = '全国ツアー' if pref == '全国' else (pref + ' ' + ('' if vv.startswith('全国ツアー') else vv)).strip()
                ndl = f"{BP.jp(nlo)}〜{BP.jp(nhi)} {tail}".strip()
            out['dateLabel'] = (dl, ndl)
    elif dl:
        out['_dateLabel_report'] = (dl, f'{s0}〜{s1}（書き方が組み立てと違う＝手で見る）')
    if s1 > (e.get('date') or ''):
        out['date'] = (e.get('date'), s1)
    return out


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    if '--selftest' in sys.argv:
        return _selftest()
    today = datetime.date.today().isoformat()
    apply = '--apply' in sys.argv
    sleep = float(sys.argv[sys.argv.index('--sleep') + 1]) if '--sleep' in sys.argv else 8.0
    text, st, end, E = load()
    by = {e['id']: e for e in E}
    if '--ids' in sys.argv:
        ids = [int(x) for x in sys.argv[sys.argv.index('--ids') + 1].split(',') if x]
    elif '--gate' in sys.argv:
        ids = []   # gate_fields O と同じ物差し（県が2つ以上・会場1つ）
        for e in E:
            if (e.get('date') or '') < today or not pia_urls(e):
                continue
            pr = e.get('prefecture') or ''
            v = e.get('venue') or ''
            if '・' in pr and '／' not in v and not v.startswith('全国ツアー'):
                ids.append(e['id'])
        lim = int(sys.argv[sys.argv.index('--limit') + 1]) if '--limit' in sys.argv else 50
        ids = ids[:lim]
    else:
        print('対象を --ids か --gate で'); return 2
    rep = io.open(REPORT, 'w', encoding='utf-8')
    fixes, ng = {}, []
    for k, i in enumerate(ids):
        e = by.get(i)
        if not e:
            continue
        htmls = []
        try:
            for j, u in enumerate(pia_urls(e)):
                if k or j:
                    time.sleep(sleep)
                h = BP.fetch(u)
                if BP.is_error_page(h):
                    raise RuntimeError('ぴあが無効化したURL ' + u)
                htmls.append(h)
        except Exception as ex:
            ng.append((i, str(ex)[:80]))
            continue
        sp = span_of(htmls, today)
        if not sp:
            ng.append((i, '枠が0（触らない）'))
            continue
        pl = plan(e, sp)
        if pl:
            fixes[i] = pl
            rep.write(f'id{i} {(e.get("name") or "")[:40]}\n')
            for f, (a, b) in pl.items():
                rep.write(f'    {f}: {a}\n      → {b}\n')
    for i, why in ng:
        rep.write(f'❌ id{i} 読めない: {why}\n')
    rep.write(f'\n=== 足す {len(fixes)}件 / 読めない {len(ng)}件 / 対象 {len(ids)}件 apply={apply} ===\n')
    rep.close()
    print(f'fill_entry_span: 足す {len(fixes)}件 / 読めない {len(ng)} / 対象 {len(ids)} → {REPORT}')
    if apply and fixes:
        text, st, end, E = load()   # 読んでいる間にほかの道具が書いているかもしれない＝読み直してその欄だけ
        for e in E:
            for f, (a, b) in (fixes.get(e['id']) or {}).items():
                if f.startswith('_') or e.get(f) != a:
                    continue   # 前と違う（だれかが直した）欄は触らない
                e[f] = b
        save(text, st, end, E)
        print('書いた')
    return 0


def _selftest():
    e = {'id': 5162, 'date': '2027-02-10', 'dateLabel': '2027年2月6日(土) 福岡 DRUM Be-1',
         'venue': '全国ツアー（DRUM Be-1／HEAVEN’S ROCK さいたま新都心 VJ-3／Zepp DiverCity（TOKYO）／BIGCAT）',
         'prefecture': '福岡・宮城・大阪・埼玉・広島'}
    sp = (['HEAVEN’S ROCK さいたま新都心 VJ-3', 'Zepp DiverCity（TOKYO）', 'DRUM Be-1', 'LIVE VANQUISH', '仙台 darwin', 'BIGCAT'],
          ['埼玉', '東京', '福岡', '広島', '宮城', '大阪'], '2027-01-14', '2027-02-10')
    pl = plan(e, sp)
    assert pl['venue'][1].endswith('／LIVE VANQUISH／仙台 darwin）'), pl
    assert pl['prefecture'][1] == '全国', pl
    assert pl['dateLabel'][1] == '2027年1月14日(木)〜2027年2月10日(水) 全国ツアー', pl
    assert 'date' not in pl
    e2 = {'id': 1, 'date': '2027-02-21', 'dateLabel': '2027年2月21日(日) 神奈川 横浜みなとみらいホール 大ホール',
          'venue': '横浜みなとみらいホール 大ホール', 'prefecture': '神奈川'}
    pl2 = plan(e2, (['横浜みなとみらいホール 大ホール', 'サントリーホール 大ホール'], ['神奈川', '東京'], '2027-02-21', '2027-02-22'))
    assert pl2['venue'][1] == '全国ツアー（横浜みなとみらいホール 大ホール／サントリーホール 大ホール）', pl2
    assert pl2['prefecture'][1] == '神奈川・東京' and pl2['date'][1] == '2027-02-22', pl2
    assert pl2['dateLabel'][1] == '2027年2月21日(日)〜2027年2月22日(月) 神奈川・東京', pl2
    assert plan(e2, (['横浜みなとみらいホール 大ホール'], ['神奈川'], '2027-02-21', '2027-02-21')) == {}
    # 今日の生ページ（5162 山本彩の5本）で通す
    S = ROOT + 'tmp/x1104/spot/raw1/'
    fs = [S + f'pia_{c}.html' for c in ('2631472', '2629413', '2634240', '2628427', '2631159')]
    if all(os.path.exists(f) for f in fs):
        BP.fill_when_from_ticketinfo = lambda rows: None   # 券種ページを取りに行かない
        sp3 = span_of([io.open(f, encoding='utf-8').read() for f in fs], '2026-11-04')
        pl3 = plan(e, sp3)
        print('  実物 5162:', json.dumps(pl3, ensure_ascii=False))
        assert pl3['dateLabel'][1].startswith('2027年1月14日(木)〜2027年2月10日(水)'), pl3
        assert 'LIVE VANQUISH' in pl3['venue'][1] and '仙台 darwin' in pl3['venue'][1], pl3
    print('selftest OK: 会場・県・会期を足すだけ（5162 山本彩・24203 ブダペスト祝祭管の形）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
