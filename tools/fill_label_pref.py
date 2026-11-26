# -*- coding: utf-8 -*-
"""会期の行（dateLabel）の後ろの県の並びに、これからの公演の枠の県を足す（2026-11-26 新設・抜き打ち 27303『ファクト』）。

  python tools/fill_label_pref.py            … 下見（tmp/fill_label_pref.txt）・直す件があれば exit 1
  python tools/fill_label_pref.py --apply    … 書く（鍵は呼ぶ側が持つ＝prepush の中。自分では取らない）
  python tools/fill_label_pref.py --selftest

## なぜ要るか
- 27303『ファクト』＝県の欄は「東京・福岡・大阪」なのに、会期の行は「2027年2月7日(日)〜2027年3月22日(月) 東京・福岡」。
  大阪 森ノ宮ピロティホール（R9年 3/10〜3/15）の公演が画面の会期の行に出ていなかった。
- 県の欄は fill_entry_pref が枠の括弧から足すが、会期の行は fill_entry_span が「会期が伸びた時」しか書き直さない
  ＝あとから受付（県）だけが足されたカードは、会期の行の県が抜けたまま（11/26 に 51件・全部ぴあ）。

## 決まり（組み立て build_pia_entries と同じ・2026-08-03 すちこ確定）
- 書き直すのは、会期の行が組み立ての形（YYYY年M月D日(曜)〜YYYY年M月D日(曜) 県・県）で、後ろが**県の名前だけ**の並びの時だけ
  （会場名つき・「全国ツアー」・配信・ほかの書き方は触らない）
- 足すのは、**これからの公演**の枠（括弧の公演日が今日以降）の括弧にある県だけ（終わった公演・県の欄だけの県は足さない）
- 4県までは「東京・福岡・大阪」と並べる。足して5県以上になる時は「全国ツアー」
- 会場名（venue）は枠に書いていない＝ここでは足さない（ぴあのページを読む fill_entry_span --ids の仕事）
"""
import datetime, io, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compact_events as C   # noqa: E402
import gate_fields as GF     # noqa: E402

ROOT = 'C:/Users/user/oshinavi/'
REPORT = ROOT + 'tmp/fill_label_pref.txt'
PREF_ENUM_MAX = 4
PREFS = set('北海道 青森 岩手 宮城 秋田 山形 福島 茨城 栃木 群馬 埼玉 千葉 東京 神奈川 新潟 富山 石川 福井 山梨 長野 岐阜 静岡 愛知 三重 '
            '滋賀 京都 大阪 兵庫 奈良 和歌山 鳥取 島根 岡山 広島 山口 徳島 香川 愛媛 高知 福岡 佐賀 長崎 熊本 大分 宮崎 鹿児島 沖縄'.split())
DL = re.compile(r'^(\d{4})年(\d{1,2})月(\d{1,2})日\([^)]\)〜(\d{4})年(\d{1,2})月(\d{1,2})日\([^)]\) (\S+)$')
SLOT_PREF = re.compile(r'（([^（）\s]+?)\s')


def new_label(e, today):
    """書き直した dateLabel。直すものが無ければ None"""
    m = DL.match(e.get('dateLabel') or '')
    if not m:
        return None
    tail = m.group(7)
    tp = tail.split('・')
    if not all(x in PREFS for x in tp):
        return None
    lo = '%s-%02d-%02d' % (m.group(1), int(m.group(2)), int(m.group(3)))
    hi = '%s-%02d-%02d' % (m.group(4), int(m.group(5)), int(m.group(6)))
    add = []
    for t in e.get('tickets') or []:
        sp = GF.slot_span(t, lo, hi)
        if not sp or sp[1] < today:
            continue
        pm = SLOT_PREF.search(t.get('type') or '')
        if not pm:
            continue
        for p in pm.group(1).split('・'):
            if p in PREFS and p not in tp and p not in add:
                add.append(p)
    if not add:
        return None
    allp = tp + add
    nt = '全国ツアー' if len(allp) > PREF_ENUM_MAX else '・'.join(allp)
    return e['dateLabel'][:m.start(7)] + nt


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    if '--selftest' in sys.argv:
        return _selftest()
    apply = '--apply' in sys.argv
    today = datetime.date.today().isoformat()
    h = io.open(ROOT + 'index.html', encoding='utf-8', newline='').read()
    comp = C.is_compact(h)
    a, b, _ = C.locate(h)
    E = C.load(h)
    ch = []
    for e in E:
        if (e.get('date') or '') < today:
            continue
        nl_ = new_label(e, today)
        if nl_:
            ch.append((e, e['dateLabel'], nl_))
    rep = io.open(REPORT, 'w', encoding='utf-8')
    rep.write('=== fill_label_pref (today=%s) 直す %d件 apply=%s ===\n' % (today, len(ch), apply))
    for e, o, n in ch:
        rep.write('id%-6s %s\n    %s\n  → %s\n' % (e['id'], (e.get('name') or '')[:40], o, n))
    rep.close()
    if apply and ch:
        for e, o, n in ch:
            e['dateLabel'] = n
        nl = '\r\n' if '\r\n' in h[:5000] else '\n'
        io.open(ROOT + 'index.html', 'w', encoding='utf-8', newline='').write(h[:a] + C.dump(E, comp, nl) + h[b:])
    print('fill_label_pref: 直す %d件 / apply=%s → %s' % (len(ch), apply, REPORT))
    return 1 if (ch and not apply) else 0


def _selftest():
    today = '2026-11-26'
    ok = True
    def check(name, got, want):
        nonlocal ok
        print(('OK ' if got == want else 'NG ') + name + ('' if got == want else '  got=%r want=%r' % (got, want)))
        ok = ok and got == want
    e = {'id': 1, 'dateLabel': '2027年2月7日(日)〜2027年3月22日(月) 東京・福岡', 'tickets': [
        {'type': '先行（大阪 R9年 3/10〜3/15公演）〜11/23 23:59', 'date': '2026-11-23'},
        {'type': '一般発売（東京 R9年 2/7〜2/28公演）〜2/25 23:59', 'date': '2027-02-25'}]}
    check('27303 大阪を足す', new_label(e, today), '2027年2月7日(日)〜2027年3月22日(月) 東京・福岡・大阪')
    e2 = dict(e, dateLabel='2027年2月7日(日)〜2027年3月22日(月) 東京・福岡・愛知・宮城')
    check('5県以上は全国ツアー', new_label(e2, today), '2027年2月7日(日)〜2027年3月22日(月) 全国ツアー')
    e3 = dict(e, dateLabel='2027年2月7日(日)〜2027年3月22日(月) 東京 PARCO劇場')
    check('会場名つきは触らない', new_label(e3, today), None)
    e4 = {'id': 4, 'dateLabel': '2026年10月1日(木)〜2027年3月22日(月) 東京', 'tickets': [
        {'type': '一般発売（大阪 10/5公演）〜10/1 23:59', 'date': '2026-10-01'}]}
    check('終わった公演の県は足さない', new_label(e4, today), None)
    print('selftest', 'OK' if ok else 'NG')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
