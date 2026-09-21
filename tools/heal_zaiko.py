# -*- coding: utf-8 -*-
"""番人（gate_zaiko_slots）が出したZAIKOの食い違いを、実ページから作り直して当てる。

  python tools/heal_zaiko.py                 … 下見（何をどう直すか出すだけ）
  python tools/heal_zaiko.py --apply         … 当てる
  python tools/heal_zaiko.py --ids 20464,20469
  python tools/heal_zaiko.py --selftest

## 決まり
- 🚨**取り直しが空の件は触らない**（消さない）。売り場が一時的に落ちているだけのことがある
- 🚨**売り切れ・販売終了の印がついた枠は、取り直しに無くても残す**
  （[[feedback_soldout_keep_visible]]＝「予定枚数終了」で出し続けるのが方針）。
  ただし**取り直し側に同じ枠が売り切れとして出てきたら、そちらに置き換える**（印が正しく付く）
- 🚨当てたら **HEADと枠数を突き合わせて、本当に減った件だけを見る**
  （[[feedback_heal_flattens_ticket_types]]／券種名が書き換わっただけでも「消えた」と出る道具があるので
   tmp/x0921/heal_tiget_compare.py と同じ切り分けをする）
"""
import argparse
import collections
import datetime
import io
import json
import re
import sys
import time

sys.path.insert(0, 'tools')
import build_zaiko_entries as BZ          # noqa: E402
import gate_zaiko_slots as GZ             # noqa: E402
import zaiko_harvest as ZH                # noqa: E402

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

PATH = 'index.html'
REPORT = 'tmp/heal_zaiko_report.txt'


def merge_slots(old, new):
    """取り直し（new）を土台に、**古い側にしか無い売り切れ・販売終了の枠を足す**。
    ＝足し算（[[feedback_heal_flattens_ticket_types]]の「手で当てる時は足し算」と同じ考え）。"""
    keys = {GZ.key(t) for t in new}
    # 券種名から日付部分を落とした骨格でも見る（「〜9/30」→「」に書き換わっただけを二重に残さない）
    def bone(t):
        return re.sub(r'〜[^|]*$', '', (t.get('type') or '')).strip()
    bones = {bone(t) for t in new}
    out = list(new)
    for t in old:
        if GZ.key(t) in keys:
            continue
        if not (t.get('soldout') or t.get('saleEnded')):
            continue          # 印の無い枠は取り直し側が正
        if bone(t) in bones:
            continue          # 同じ券種が取り直し側にある＝そちらが新しい
        out.append(t)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--ids', default='')
    ap.add_argument('--sleep', type=float, default=0.5)
    # 🚨作り直し用＝**足し算せず取り直しで丸ごと置き換える**。
    #   券種名の作り方そのものを直した時（2026-09-21 ref_name へ）は、古い名前の枠を
    #   「売り切れだから残す」と足してしまうと**ニセの券種名が残る**ので置き換えが正しい。
    #   ⚠️枠が減る件は報告に出す（[[feedback_heal_flattens_ticket_types]]）。
    ap.add_argument('--replace', action='store_true')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        return _selftest()

    today = datetime.date.today().isoformat()
    ids = {int(x) for x in re.findall(r'\d+', a.ids)} or None
    h = io.open(PATH, encoding='utf-8', newline='').read()
    NL = '\r\n' if '\r\n' in h else '\n'
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
    EVENTS = json.loads(m.group(2))

    target = []
    for e in EVENTS:
        u = (e.get('links') or {}).get('zaiko')
        if not u:
            continue
        if ids and e['id'] not in ids:
            continue
        target.append((e, u))
    if not target:
        print('対象が無い')
        return 0

    rep = io.open(REPORT, 'w', encoding='utf-8')
    rep.write('=== heal_zaiko (today=%s) 対象%d件 ===\n\n' % (today, len(target)))
    healed, empty, ferr, same = [], [], [], 0
    for i, (e, u) in enumerate(target, 1):
        d = ZH.parse_event(ZH.fetch(u), u)
        if d is None:
            ferr.append(e['id'])
            time.sleep(a.sleep)
            continue
        row = GZ.listrow_from_entry(e, u)
        built, _ = BZ.build_one(row, d, today, collections.Counter())
        new = (built or {}).get('tickets') or []
        if not new:
            empty.append(e['id'])           # 🚨取り直しが空＝触らない（消さない）
            time.sleep(a.sleep)
            continue
        old = e.get('tickets') or []
        merged = new if a.replace else merge_slots(old, new)
        if {GZ.key(t) for t in merged} == {GZ.key(t) for t in old}:
            same += 1
        else:
            healed.append((e, old, merged))
            rep.write('id%-6s %s @ %s\n    %s\n'
                      % (e['id'], (e.get('name') or '')[:40], (e.get('venue') or '')[:20], u))
            for t in old:
                if GZ.key(t) not in {GZ.key(x) for x in merged}:
                    rep.write('    - 外す: %s\n' % (t.get('type') or '')[:70])
            for t in merged:
                if GZ.key(t) not in {GZ.key(x) for x in old}:
                    rep.write('    + 足す: %s%s\n' % ((t.get('type') or '')[:70],
                                                     '（売り切れ印）' if t.get('soldout') else ''))
        if i % 50 == 0:
            print('  見た %d/%d件' % (i, len(target)))
        time.sleep(a.sleep)

    rep.write('\n=== %d件のうち 当てる %d / 変化なし %d / 取り直しが空 %d / 読めなかった %d ===\n'
              % (len(target), len(healed), same, len(empty), len(ferr)))
    if empty:
        rep.write('取り直しが空（触っていない）: %s\n' % empty[:20])
    if ferr:
        rep.write('読めなかった（触っていない）: %s\n' % ferr[:20])

    if a.apply and healed:
        byid = {e['id']: mg for e, _, mg in healed}
        for e in EVENTS:
            if e['id'] in byid:
                e['tickets'] = byid[e['id']]
        bak = 'index.html.bak_%s_zaikoheal' % datetime.date.today().strftime('%m%d')
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
    print('heal_zaiko: 当てる%d / 変化なし%d / 空%d / 読めなかった%d / apply=%s → %s'
          % (len(healed), same, len(empty), len(ferr), a.apply, REPORT))
    return 0


def _selftest():
    live = {'type': 'チケット（東京 9/21公演）販売中', 'date': '2026-09-21',
            'saleEndUnknown': True, 'url': 'u'}
    sold = {'type': 'チケット（東京 9/21公演）', 'date': '2026-09-21',
            'soldout': True, 'url': 'u'}
    other_sold = {'type': 'VIP（東京 9/21公演）', 'date': '2026-09-21',
                  'soldout': True, 'url': 'u'}
    # ① 売り切れに変わった＝取り直し側に置き換わる（古い「販売中」は残さない）
    out = merge_slots([live], [sold])
    assert out == [sold], out
    # ② 古い側にしか無い売り切れ枠は**残す**（売り場から消えても出し続ける）
    out2 = merge_slots([other_sold], [sold])
    assert sold in out2 and other_sold in out2, out2
    # ③ 印の無い枠は取り直し側が正＝古い分は落とす
    out3 = merge_slots([dict(live, type='旧（東京 9/21公演）販売中')], [sold])
    assert out3 == [sold], out3
    print('selftest OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
