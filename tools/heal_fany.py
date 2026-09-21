# -*- coding: utf-8 -*-
"""FANY由来エントリ（1公演＝1エントリ）の枠を、**最新の一覧から作り直して差し替える**（FANY版のヒール）。

  python tools/heal_fany.py --src tmp/fany_MMDD.json            … 下見（何をどう直すか出すだけ）
  python tools/heal_fany.py --src tmp/fany_MMDD.json --apply    … 当てる
  python tools/heal_fany.py --src tmp/fany_MMDD.json --ids 19745,19097
  python tools/heal_fany.py                                     … 一覧を引き直してから下見
  python tools/heal_fany.py --selftest

毎朝の型＝**番人 → heal_fany --apply → 番人**（同じ一覧 `--src` を3回とも使う）:
  python tools/gate_fany_slots.py --src tmp/fany_MMDD.json
  python tools/heal_fany.py --src tmp/fany_MMDD.json --apply
  python tools/gate_fany_slots.py --src tmp/fany_MMDD.json   … 残りは「今日の公演」だけのはず

## なぜ要るか（2026-09-21 夜に新設）

FANYも毎日ずれる。9/21夜の番人で、**本日10:00/11:00/12:00に発売になった枠が
登録上は「9/21 HH:MM発売」のまま**（売り場は「〜締切」の発売中）が43件、
先行が終わったのに印が無いのが1件あった。放っておくと明日「締切が過ぎた枠」に見えて
買える枠0の削除候補に上がる。ぴあのヒールはFANYを見ないので、これが要る。

## 作り直し方

`gate_fany_slots.py` と**同じ関数**（build_fany_entries.build_one、同日複数公演の数え方も同じ）で
公演ごとに枠を作る＝番人と同じ物差しなので、当てた後に番人を回せば一致する。
公演の突き合わせは**公演id**（各枠の url `/reception/<sales_id>/<performance_id>` と一覧の `id`）。

## 守ること

- **tickets だけ**差し替える。venue・dateLabel・artist・genre・名前は触らない（手直しが巻き戻る）
- FANY以外の売り場の枠（url が ticket.fany.lol でない枠）は残す
- 対象＝links.fany があり、FANYの申込URLを持つエントリ。**リンクだけ足したぴあ等の登録は対象外**
- 🚨安全弁①＝**一覧に公演が無い（落ちた・今日の公演）エントリは触らない**
- 🚨安全弁②＝作り直しで**印の無い枠（買える／発売前）が消える**件は当てずに報告
  （一覧の取りこぼし・混雑の疑い。券種名の頭＝「券種（県 M/D公演）」が作り直し側に残っていれば
   「発売→締切に変わっただけ」とみなす）
- 🚨安全弁③＝**売り切れ・先行終了・販売終了の印付き枠は、作り直しに無くても残す**
  （[[feedback_soldout_keep_visible]]）。同じ券種が作り直し側にあればそちらが新しい
- 作り直し前と同じ枠は、古い方の soldoutSince 等を引き継ぐ（印の付いた日を今日に書き換えない）
- 🚨FANYに「予定枚数終了」の文言は無い＝完売はここで作らない（build_one の対応表どおり）
"""
import argparse
import collections
import datetime
import io
import json
import re
import sys

sys.path.insert(0, 'tools')
import build_fany_entries as BF          # noqa: E402
import gate_fany_slots as GF             # noqa: E402
import fany_harvest as FH                # noqa: E402

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

PATH = 'index.html'
REPORT = 'tmp/heal_fany_report.txt'
RE_PERF = re.compile(r'ticket\.fany\.lol/reception/\d+/(\d+)')


def is_fany(t):
    return 'ticket.fany.lol' in (t.get('url') or '')


def marked(t):
    return bool(t.get('soldout') or t.get('saleEnded') or t.get('presaleEnded'))


def bone(t):
    """券種名の頭＝「券種（県 M/D公演）」まで。発売→締切・締切の延長で後ろが変わっても同じ枠と見る。"""
    ty = t.get('type') or ''
    i = ty.find('公演）')
    return ty[:i + 3] if i >= 0 else re.sub(r'(\d+/\d+ [\d:]*発売)?(〜.*)?$', '', ty).strip()


def heal_one(old_fany, new):
    """(merged, lost) を返す。lost＝作り直しで消える印の無い枠（あれば当てない）。"""
    old_by_key = {GF.key(t): t for t in old_fany}
    new_bones = {bone(t) for t in new}
    merged = []
    for t in new:
        o = old_by_key.get(GF.key(t))
        if o is not None:
            keep = dict(o)
            keep['url'] = t.get('url') or o.get('url')
            merged.append(keep)
        else:
            merged.append(t)
    mkeys = {GF.key(t) for t in merged}
    lost = []
    for t in old_fany:
        if GF.key(t) in mkeys or bone(t) in new_bones:
            continue
        if marked(t):
            merged.append(t)          # ③ 印付きは残す
        else:
            lost.append(t)            # ② 印なしが消える
    return merged, lost


def build_page(data, today):
    """一覧から 公演id → 作り直した枠 の対応を作る（番人と同じ組み方）。"""
    gmap = dict(data.get('genre_map') or {})
    same = collections.Counter()
    for p in data['performances']:
        iso = BF.perf_date_iso(p)
        if iso:
            same[(p.get('event_id'), iso, p.get('venue_id'))] += 1
    gmap['_same_day'] = same
    page, none = {}, {}
    for p in data['performances']:
        e, why = BF.build_one(p, today, gmap, collections.Counter())
        if e:
            page[str(p.get('id'))] = e['tickets']
        else:
            none[str(p.get('id'))] = why
    return page, none


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', default=None, help='引いてある一覧JSON（無ければ引き直す）')
    ap.add_argument('--ids', default='')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--days', type=int, default=200)
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        return _selftest()

    today = datetime.date.today().isoformat()
    ids = {int(x) for x in re.findall(r'\d+', a.ids)} or None
    if a.src:
        data = json.load(open(a.src, encoding='utf-8'))
    else:
        tmp = 'tmp/fany_heal_%s.json' % datetime.date.today().strftime('%m%d')
        to = (datetime.date.today() + datetime.timedelta(days=a.days)).isoformat()
        if FH.harvest(today, to, tmp) != 0:
            print('🚨一覧が引けなかった＝何も触らない')
            return 2
        data = json.load(open(tmp, encoding='utf-8'))
    page, none = build_page(data, today)

    h = io.open(PATH, encoding='utf-8', newline='').read()
    NL = '\r\n' if '\r\n' in h else '\n'
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
    EVENTS = json.loads(m.group(2))

    rep = io.open(REPORT, 'w', encoding='utf-8')
    rep.write('=== heal_fany (today=%s) src=%s ===\n\n' % (today, a.src or 'refetch'))
    healed, same, gone, stopped, multi, empty, linkonly = [], 0, [], [], [], [], 0
    for e in EVENTS:
        if not (e.get('links') or {}).get('fany'):
            continue
        if ids and e['id'] not in ids:
            continue
        tickets = e.get('tickets') or []
        old_fany = [t for t in tickets if is_fany(t)]
        if not old_fany:
            linkonly += 1               # リンクだけ足した登録＝対象外
            continue
        perfs = {p for t in old_fany for p in RE_PERF.findall(t.get('url') or '')}
        if len(perfs) != 1:
            multi.append((e, sorted(perfs)))
            continue
        pid = perfs.pop()
        if pid not in page:
            if pid in none:
                empty.append((e, none[pid]))   # 作り直しが空＝触らない
            else:
                gone.append(e)                 # ① 一覧に無い＝触らない
            continue
        merged, lost = heal_one(old_fany, page[pid])
        if lost:
            stopped.append((e, lost))          # ② 当てない
            continue
        if {GF.key(t) for t in merged} == {GF.key(t) for t in old_fany}:
            same += 1
            continue
        others = [t for t in tickets if not is_fany(t)]
        healed.append((e, old_fany, others + merged))

    for e, old, new in healed:
        rep.write('id%-6s %s @ %s 公演%s\n' % (e['id'], (e.get('name') or '')[:36],
                                             (e.get('venue') or '')[:18], e.get('date')))
        nk, ok = {GF.key(t) for t in new}, {GF.key(t) for t in old}
        for t in old:
            if GF.key(t) not in nk:
                rep.write('    - 外す: %s\n' % (t.get('type') or '')[:80])
        for t in new:
            if GF.key(t) not in ok:
                rep.write('    + 足す: %s%s\n' % ((t.get('type') or '')[:80],
                                                 '（印付き）' if marked(t) else ''))
    rep.write('\n--- ⚠️安全弁②で止めた（印なしの枠が消える）---\n')
    for e, lost in stopped:
        rep.write('id%-6s %s 公演%s\n' % (e['id'], (e.get('name') or '')[:40], e.get('date')))
        for t in lost:
            rep.write('    消えるはずだった: %s\n' % (t.get('type') or '')[:80])
    rep.write('\n--- 公演idが1つに決まらない（触っていない）---\n')
    for e, ps in multi:
        rep.write('id%-6s %s %s\n' % (e['id'], (e.get('name') or '')[:40], ps))
    rep.write('\n--- 作り直しが空（触っていない）---\n')
    for e, why in empty:
        rep.write('id%-6s 公演%s %s … %s\n' % (e['id'], e.get('date'), (e.get('name') or '')[:40], why))
    rep.write('\n--- 一覧に無い＝落ちた・今日の公演（触っていない）%d件 ---\n' % len(gone))
    for e in gone:
        rep.write('id%-6s 公演%s %s\n' % (e['id'], e.get('date'), (e.get('name') or '')[:40]))
    nslots = sum(len([t for t in new if is_fany(t)]) for _, _, new in healed)
    summary = ('当てる %d件（差し替え後のFANY枠 %d枠）/ 変化なし %d / 安全弁②で止めた %d / '
               '一覧に無い %d / 作り直し空 %d / 公演id複数 %d / リンクだけ(対象外) %d'
               % (len(healed), nslots, same, len(stopped), len(gone), len(empty), len(multi), linkonly))
    rep.write('\n=== %s ===\n' % summary)

    if a.apply and healed:
        byid = {e['id']: new for e, _, new in healed}
        for e in EVENTS:
            if e['id'] in byid:
                e['tickets'] = byid[e['id']]
        bak = 'index.html.bak_%s_fanyheal' % datetime.date.today().strftime('%m%d')
        io.open(bak, 'w', encoding='utf-8', newline='').write(h)
        io.open(PATH, 'w', encoding='utf-8', newline='').write(
            h[:m.start()] + m.group(1)
            + json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
            + m.group(3) + h[m.end():])
        raw = open(PATH, 'rb').read()
        rep.write('当てた %d件 / backup %s\n' % (len(healed), bak))
        rep.write('CRCRLF %d / 素のLF %d （どちらも0が正）\n'
                  % (raw.count(b'\r\r\n'), len(re.findall(rb'(?<!\r)\n', raw))))
    rep.close()
    print('heal_fany: %s / apply=%s → %s' % (summary, a.apply, REPORT))
    return 0


def _selftest():
    u = 'https://ticket.fany.lol/reception/1/100'
    pre = {'type': '一般発売（大阪 10/16公演）9/21 10:00発売', 'date': '2026-09-21',
           'startDate': '2026-09-21', 'url': u}
    live = {'type': '一般発売（大阪 10/16公演）9/21 10:00発売〜10/15 23:59', 'date': '2026-10-15',
            'startDate': '2026-09-21', 'url': u}
    sold_old = {'type': '先行（大阪 10/16公演）〜8/31 11:00', 'date': '2026-08-31', 'url': u,
                'soldout': True, 'soldoutSince': '2026-09-01', 'presaleEnded': True}
    ok = True

    def check(label, cond):
        nonlocal ok
        ok &= bool(cond)
        print('%s %s' % ('OK' if cond else 'NG', label))

    # ① 発売前→発売中に変わった＝置き換わる（止めない）
    mg, lost = heal_one([pre], [live])
    check('発売前→発売中は置き換える', mg == [live] and not lost)
    # ② 印なしの枠が作り直しから消える＝止める
    other = {'type': '当日券（大阪 10/16公演）〜10/16', 'date': '2026-10-16', 'url': u}
    mg, lost = heal_one([pre, other], [live])
    check('印なしの枠が消える件は止める', lost == [other])
    # ③ 印付きの枠は作り直しに無くても残す
    mg, lost = heal_one([live, sold_old], [live])
    check('売り切れ・先行終了の印付きは残す', sold_old in mg and not lost)
    # ④ 同じ枠は古い soldoutSince を引き継ぐ
    sold_new = dict(sold_old, soldoutSince='2026-09-21')
    mg, lost = heal_one([sold_old], [sold_new])
    check('同じ枠は古い soldoutSince を引き継ぐ', mg[0]['soldoutSince'] == '2026-09-01')
    # ⑤ 印なし→先行終了の印が付いた（同じ券種）＝置き換える
    p1 = {'type': 'FANY IDメンバー抽選先行（大阪 10/31公演）〜9/21 11:00', 'date': '2026-09-21', 'url': u}
    p2 = dict(p1, soldout=True, soldoutSince='2026-09-21', presaleEnded=True)
    mg, lost = heal_one([p1], [p2])
    check('先行が終わって印が付いたら置き換える', mg == [p2] and not lost)
    # ⑥ 券種名の頭の取り方
    check('券種名の頭', bone(live) == '一般発売（大阪 10/16公演）')
    print('selftest %s' % ('OK' if ok else 'NG'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
