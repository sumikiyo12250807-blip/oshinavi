# -*- coding: utf-8 -*-
"""会期（dateLabel）を、まだ出ている枠の括弧に書いた公演日で**伸ばすだけ**（売り場を叩かない・縮めない）。

  python tools/fill_span_from_slots.py            … 下見（tmp/fill_span_from_slots.txt）
  python tools/fill_span_from_slots.py --apply    … 書く（書く直前に読み直し、dateLabel が下見の時と同じ件だけ）
  python tools/fill_span_from_slots.py --ids 31897 [--apply]
  python tools/fill_span_from_slots.py --selftest

## なぜ要るか（2026-11-05 抜き打ち 31897 海宝直人・すちこ「こんな間違いがあるゲートは信用できない」）
- 10/15 朝の足し込みで、FC先行のページ（1/4〜1/5）で作ったエントリに一般発売の枠（12/19〜1/5）を足した。
  最後の公演日（date）は合っていたが、会期の表示の「始まり」は誰も直さなかった＝カードは 1/4〜1/5 のまま。
- gate_fields の P（会期の外に枠）は 11/4 に足したが「件数だけ・止めない」で、199件が出たまま放っていた。
- fill_entry_span はぴあのページを読む・--gate は県2つ以上の型（O）しか拾わない＝P は直らなかった。
## やること
gate_fields と同じ物差し（P）で、組み立ての書き方（YYYY年M月D日(曜)〜…）の会期だけ、
初日を前へ・千秋楽を後ろへ伸ばす（後ろの「県 会場」はそのまま）。date も千秋楽まで伸ばす。会場・県は fill_entry_pref／fill_entry_span の仕事。
"""
import datetime, io, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gate_fields as GF  # noqa: E402

ROOT = 'C:/Users/user/oshinavi/'
REPORT = ROOT + 'tmp/fill_span_from_slots.txt'
DL = re.compile(r'^(\d{4})年(\d{1,2})月(\d{1,2})日\([^)]\)(?:〜(\d{4})年(\d{1,2})月(\d{1,2})日\([^)]\))?((?:\s.*)?)$')
WD = '月火水木金土日'


def jp(d):
    y, m, dd = map(int, d.split('-'))
    return f'{y}年{m}月{dd}日({WD[datetime.date(y, m, dd).weekday()]})'


def plan(e, today):
    """伸ばす中身 {欄: (前, 後)}／伸ばさない時 None／🆕会期のどこにも枠が無い時 {'_report': ...}（会期の側が違う疑い＝手で見る）"""
    m = DL.match(e.get('dateLabel') or '')
    if not m:
        return None
    lo = '%s-%02d-%02d' % (m.group(1), int(m.group(2)), int(m.group(3)))
    hi = ('%s-%02d-%02d' % (m.group(4), int(m.group(5)), int(m.group(6)))) if m.group(4) else lo
    nlo, nhi = lo, hi
    anchored = False
    spans = []
    for t in e.get('tickets') or []:
        if not (t.get('soldout') or t.get('saleUntilSoldOut') or (t.get('date') or '') >= today):
            continue
        sp = GF.slot_span(t, lo, hi)   # 🆕11/5 年の書いていない括弧は 1年後で会期に入るならそちら（TIGET 45783 ほか）
        if not sp or sp[1] < today or sp[0] > sp[1]:
            continue
        spans.append(sp)
        if sp[0] <= hi and sp[1] >= lo:
            anchored = True   # 会期と重なる枠がある＝今の会期は枠に裏付けがある
        nlo, nhi = min(nlo, sp[0]), max(nhi, sp[1])
    if (nlo, nhi) == (lo, hi):
        return None
    if not anchored and hi >= today:
        # （会期がもう終わっている＝元の公演が済んで、あとから足された公演だけ残っている型は伸ばしてよい＝650 木村至信 8/29 → 11/28）
        # 🆕2026-11-05 42719＝枠は 12/12・会期と date は 12/19＝会期の側が違う。伸ばすと嘘が増える＝触らず報告
        return {'_report': (e.get('dateLabel'), f'会期 {lo}〜{hi} に重なる枠が無い（枠 {min(s[0] for s in spans)}〜{max(s[1] for s in spans)}）＝会期か枠の公演日が違う疑い・売り場で見る')}
    ndl = (jp(nlo) if nlo == nhi else f'{jp(nlo)}〜{jp(nhi)}') + (m.group(7) or '')
    out = {'dateLabel': (e.get('dateLabel'), ndl)}
    if nhi > (e.get('date') or ''):
        out['date'] = (e.get('date'), nhi)
    return out


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    if '--selftest' in sys.argv:
        return _selftest()
    today = datetime.date.today().isoformat()
    path = ROOT + 'index.html'
    text = io.open(path, encoding='utf-8', newline='').read()
    mm = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
    E, end = json.JSONDecoder().raw_decode(text, mm.start(1))
    ids = None
    if '--ids' in sys.argv:
        ids = {int(x) for x in sys.argv[sys.argv.index('--ids') + 1].split(',') if x}
    fixes = {}
    for e in E:
        if ids is not None and e['id'] not in ids:
            continue
        if (e.get('date') or '') < today:
            continue
        p = plan(e, today)
        if p:
            fixes[e['id']] = (e, p)
    rep = io.open(REPORT, 'w', encoding='utf-8')
    for i, (e, p) in fixes.items():
        rep.write(f'id{i} {(e.get("name") or "")[:40]}\n')
        for f, (a, b) in p.items():
            rep.write(f'    {f}: {a}\n      → {b}\n')
    nrep = sum(1 for _, p in fixes.values() if '_report' in p)
    rep.write(f'\n=== 伸ばす {len(fixes) - nrep}件 / 手で見る（会期に重なる枠なし）{nrep}件 apply={"--apply" in sys.argv} ===\n')
    rep.close()
    print(f'fill_span_from_slots: 伸ばす {len(fixes) - nrep}件 / 手で見る {nrep}件 → {REPORT}')
    if '--apply' in sys.argv and fixes:
        n = 0
        for e in E:
            if e['id'] in fixes:
                for f, (a, b) in fixes[e['id']][1].items():
                    if not f.startswith('_') and e.get(f) == a:
                        e[f] = b
                        n += 1
        compact = text[mm.start(1):mm.start(1) + 3] in ('[\r\n', '[\n{') or text[mm.start(1):mm.start(1) + 4].startswith('[\r\n{')
        body = ('[\n' + ',\n'.join(json.dumps(x, ensure_ascii=False, separators=(',', ':')) for x in E) + '\n]') if compact \
            else json.dumps(E, ensure_ascii=False, indent=2)
        if '\r\n' in text[mm.start(1):mm.start(1) + 3000]:
            body = body.replace('\r\n', '\n').replace('\n', '\r\n')
        io.open(path, 'wb').write((text[:mm.start(1)] + body + text[end:]).encode('utf-8'))
        print(f'書いた 欄{n}')
    return 0


def _selftest():
    today = '2026-11-05'
    e = {'id': 31897, 'date': '2027-01-05', 'dateLabel': '2027年1月4日(月)〜2027年1月5日(火) 東京 シアタークリエ',
         'tickets': [{'type': '先行（東京 R9年 1/4〜1/5公演）〜10/22 23:59', 'date': '2026-10-22'},
                     {'type': '一般発売（東京 12/19〜R9年 1/5公演）11/25 11:00発売', 'date': '2026-11-25', 'startDate': '2026-11-25'}]}
    p = plan(e, today)
    assert p == {'dateLabel': (e['dateLabel'], '2026年12月19日(土)〜2027年1月5日(火) 東京 シアタークリエ')}, p
    e2 = {'id': 1, 'date': '2027-02-10', 'dateLabel': '2027年2月6日(土) 福岡 DRUM Be-1',
          'tickets': [{'type': '一般発売（福岡 R9年 2/6公演）〜2/1 23:59', 'date': '2027-02-01'},
                      {'type': '一般発売（埼玉 R9年 1/14公演）〜1/10 23:59', 'date': '2027-01-10'},
                      {'type': '一般発売（大阪 R9年 2/10公演）〜2/7 23:59', 'date': '2027-02-07'}]}
    p2 = plan(e2, today)
    assert p2['dateLabel'][1] == '2027年1月14日(木)〜2027年2月10日(水) 福岡 DRUM Be-1', p2
    assert 'date' not in p2
    # 終わった枠・過ぎた締切の枠では伸ばさない
    e3 = {'id': 2, 'date': '2026-12-01', 'dateLabel': '2026年12月1日(火) 東京 X',
          'tickets': [{'type': '先行（東京 11/1公演）〜10/20 23:59', 'date': '2026-10-20'}]}
    assert plan(e3, today) is None
    # 🆕年の書いていない括弧（TIGET 45783＝2027-12-30 の公演）＝伸ばさない
    e4 = {'id': 45783, 'date': '2027-12-30', 'dateLabel': '2027年12月30日(木) 大阪',
          'tickets': [{'type': '●前売りチケット（3,000円）（大阪 12/30公演）〜12/15 23:59', 'date': '2026-12-15'}]}
    assert plan(e4, today) is None, plan(e4, today)
    # 🆕会期のどこにも枠が無い（42719＝枠 12/12・会期 12/19）＝伸ばさず報告
    e5 = {'id': 42719, 'date': '2026-12-19', 'dateLabel': '2026年12月19日(土) 埼玉',
          'tickets': [{'type': '自由席（埼玉 12/12公演）〜12/12', 'date': '2026-12-12'}]}
    p5 = plan(e5, today)
    assert p5 and list(p5) == ['_report'], p5
    print('selftest OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
