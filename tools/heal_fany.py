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
  🆕2026-11-04 例外＝artist は「今の売り場の出演者が登録の名前を全部含んでもっと多い」時だけ差し替える（22821・41060＝後から足された出演者）
  　＝`--apply --artist` の時だけ書く（初回 11/4 の下見で 564件＝10/24 より前の「先頭3組」登録が大半。--artist なしは報告だけ）
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
    ARTISTS.clear()
    for p in data['performances']:
        e, why = BF.build_one(p, today, gmap, collections.Counter())
        if e:
            page[str(p.get('id'))] = e['tickets']
            ARTISTS[str(p.get('id'))] = (e.get('artist') or '', e.get('name') or '')
            DATES[str(p.get('id'))] = (e.get('date'), e.get('dateLabel'))
        else:
            none[str(p.get('id'))] = why
    return page, none


ARTISTS = {}   # 公演id → (作り直した出演者, 公演名)
DATES = {}     # 🆕11/5 公演id → (作り直したカードの date, dateLabel)
_LBL = re.compile(r'^(ゲスト|MC|ＭＣ|司会|出演)\s*[:：]\s*')


def _names(a):
    return [_LBL.sub('', x).strip() for x in (a or '').split('／') if _LBL.sub('', x).strip()]


def artist_grow(old, new, name):
    """🆕2026-11-04 抜き打ち 22821 ルミネ平日よる（5組抜け）・11/2 41060 Kiwami（滝音抜け）＝FANY は登録のあとで出演者を足す。
    ヒールは tickets だけ＝出演者は登録の時のまま。**今の売り場の出演者が、登録の名前を全部含んでもっと多い時だけ**差し替える
    （手で直した名前・並べ替えは巻き戻さない＝含まれない名前が1つでもあれば触らない）。公演名に倒れた出演者（＝old が公演名）も差し替える。"""
    if not new or new == name:
        return None
    on, nn = _names(old), _names(new)
    _k = lambda s: re.sub(r'[\s　]', '', s)
    if old == name:
        return new
    if len(nn) > len(on) and {_k(x) for x in on} <= {_k(x) for x in nn}:
        return new
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', default=None, help='引いてある一覧JSON（無ければ引き直す）')
    ap.add_argument('--ids', default='')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--artist', action='store_true', help='🆕11/4 出演者が増えた件の artist も書く（無ければ報告だけ）')
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
    artist_up = {}
    datefix = {}
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
        if len(perfs) > 1:
            # 🆕2026-10-01 同じタイトルで会場だけ違う公演を1エントリに畳んだもの（ユーザー「怪談を浴びる会は同じタイトルで
            #   県名が違うだけだからひとつにまとめて」）＝公演idごとに作り直して足し合わせる。
            #   一覧に無い・作り直しが空の公演は、その公演の枠をそのまま残す（触らない）。どこかで印なしの枠が消えるなら当てない。
            groups = collections.OrderedDict()
            for t in old_fany:
                ps = RE_PERF.findall(t.get('url') or '')
                groups.setdefault(ps[0] if ps else '', []).append(t)
            merged_all, lost_all = [], []
            for pid, grp in groups.items():
                if pid in page:
                    mg, ls = heal_one(grp, page[pid])
                    merged_all += mg
                    lost_all += ls
                else:
                    merged_all += grp
            if lost_all:
                stopped.append((e, lost_all))
                continue
            if {GF.key(t) for t in merged_all} == {GF.key(t) for t in old_fany}:
                same += 1
                continue
            healed.append((e, old_fany, [t for t in tickets if not is_fany(t)] + merged_all))
            multi.append((e, sorted(perfs)))   # 報告には残す（畳んだエントリ）
            continue
        if len(perfs) != 1:
            multi.append((e, sorted(perfs)))
            continue
        pid = perfs.pop()
        if pid in ARTISTS:
            na = artist_grow(e.get('artist') or '', ARTISTS[pid][0], e.get('name') or '')
            if na and na != e.get('artist'):
                artist_up[e['id']] = (e.get('artist'), na)
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
        # 🆕🚨2026-11-05 カードの日付も売り場に合わせる（heal_tiget と同じ穴＝受付だけ差し替えてカードの日付は古いまま）。
        #   FANY は1公演1カード＝ほかの売り場の枠が無いカードだけ
        nd = DATES.get(pid)
        if nd and nd[0] and nd[1] and not [t for t in tickets if not is_fany(t)]:
            _dp = lambda s: re.match(r'^[^\s（]*', s or '').group(0)
            # 🆕🚨2026-11-12 枠の括弧の最後の公演日より前には下げない（40941〜40943 月のパス＝売り場の公演日は月初だが枠は月末まで）
            import gate_fields as GFD
            spans = [GFD.slot_span(t) for t in merged]
            last = max((s[1] for s in spans if s), default='')
            if (nd[0] != e.get('date') or _dp(nd[1]) != _dp(e.get('dateLabel'))) and not (last and nd[0] < last):
                datefix[e['id']] = ((e.get('date'), e.get('dateLabel')), nd)
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
    rep.write('\n--- 🆕出演者が増えた（登録の名前を全部含んでもっと多い）＝差し替える %d件 ---\n' % len(artist_up))
    for i, (o, n) in artist_up.items():
        rep.write('id%-6s %s\n      → %s\n' % (i, (o or '')[:70], (n or '')[:120]))
    rep.write('\n--- 🆕カードの日付を売り場に合わせる %d件 ---\n' % len(datefix))
    for i, (o, n) in datefix.items():
        rep.write('id%-6s %s ｜ %s → %s ｜ %s\n' % (i, o[0], o[1], n[0], n[1]))
    nslots = sum(len([t for t in new if is_fany(t)]) for _, _, new in healed)
    summary = ('当てる %d件（差し替え後のFANY枠 %d枠）/ 変化なし %d / 安全弁②で止めた %d / '
               '一覧に無い %d / 作り直し空 %d / 公演id複数 %d / リンクだけ(対象外) %d / 出演者を足す %d'
               % (len(healed), nslots, same, len(stopped), len(gone), len(empty), len(multi), linkonly, len(artist_up)))
    rep.write('\n=== %s ===\n' % summary)

    if a.apply and (healed or datefix or (a.artist and artist_up)):
        byid = {e['id']: new for e, _, new in healed}
        for e in EVENTS:
            if e['id'] in byid:
                e['tickets'] = byid[e['id']]
            if e['id'] in datefix and (e.get('date'), e.get('dateLabel')) == datefix[e['id']][0]:
                e['date'], e['dateLabel'] = datefix[e['id']][1]
            if a.artist and e['id'] in artist_up and e.get('artist') == artist_up[e['id']][0]:
                e['artist'] = artist_up[e['id']][1]
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
    # ⑦ 🆕11/4 出演者が増えた時だけ差し替える（22821・41060）／手直し（含まれない名前）は巻き戻さない
    check('増えたら差し替え', artist_grow('桂かい枝／ギャロップ／セルライトスパ',
                                    '桂かい枝／ギャロップ／５ＧＡＰ／セルライトスパ／空気階段', 'ルミネ') == '桂かい枝／ギャロップ／５ＧＡＰ／セルライトスパ／空気階段')
    check('札付きの古い名前も含むと見る', artist_grow('ゲスト:カベポスター／超速バギー', '滝音／カベポスター／超速バギー', 'K') == '滝音／カベポスター／超速バギー')
    check('含まれない名前があれば触らない', artist_grow('A／手で直したB', 'A／C／D', 'n') is None)
    check('同じ数なら触らない', artist_grow('A／B', 'B／A', 'n') is None)
    check('公演名に倒れていたら差し替え', artist_grow('ルミネ', 'A／B', 'ルミネ') == 'A／B')
    check('作り直しも公演名なら触らない', artist_grow('A', 'ルミネ', 'ルミネ') is None)
    print('selftest %s' % ('OK' if ok else 'NG'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
