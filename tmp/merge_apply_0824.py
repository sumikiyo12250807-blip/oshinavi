# -*- coding: utf-8 -*-
"""再導出した枠を既存エントリに**足すだけ**当てる（2026-08-24 の統合）。

🚨 まるごと置換にしない。build_pia_entries は (公演日,会場,券種名,状態) で行を潰すので、
   手で分けた枠まで畳んでしまう（feedback_dedup_badges_keeps_urls／2026-08-23の反省）。
   既存の枠は1つも消さず、増えた分だけ append する。減る方向は報告だけして人が見る。

🚨 date（千秋楽）は自動で動かさない。代わりに、足した枠のバッジ文言から公演日を機械抽出して
   「登録の千秋楽より後ろの公演がある」ものを報告する（今朝 id=1006 喜楽館で、千秋楽の登録が
   古いまま生きた枠が残る型を踏んだ）。

入力: tmp/merge_fetched_0824.json  {entry_id: [ticket,...]}
使い方:
  python tmp/merge_apply_0824.py            # 差分を見るだけ
  python tmp/merge_apply_0824.py --apply
"""
import datetime
import io
import json
import re
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')

APPLY = '--apply' in sys.argv
PATH = 'index.html'
TODAY = datetime.date(2026, 8, 24)


def slot_key(t):
    """同じ枠かどうか＝バッジ文言＋締切＋発売日。文言が同じでも締切が違えば別の枠。"""
    return (t.get('type') or '', t.get('date') or '', t.get('startDate') or '')


def show_dates(text):
    """バッジ文言から公演日を拾う。『（東京 12/13公演）』『（東京 R9年 1/5公演）』の形。"""
    out = []
    m = re.search(r'（[^（）]*?公演）', text or '')
    if not m:
        return out
    seg = m.group(0)
    r9 = 'R9年' in seg or 'R１０年' in seg
    for mm in re.finditer(r'(?:R(\d+)年\s*)?(\d{1,2})/(\d{1,2})', seg):
        y = 2027 if (mm.group(1) == '9' or (r9 and not mm.group(1))) else 2026
        try:
            out.append(datetime.date(y, int(mm.group(2)), int(mm.group(3))))
        except ValueError:
            pass
    return out


def main():
    got = json.load(io.open('tmp/merge_fetched_0824.json', encoding='utf-8'))
    src = io.open(PATH, encoding='utf-8', newline='').read()
    nl = '\r\n' if '\r\n' in src else '\n'
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
    assert m, 'EVENTS配列が見つからない'
    events = json.loads(m.group(2))
    by = {e['id']: e for e in events}

    log = io.open('tmp/merge_diff_0824.txt', 'w', encoding='utf-8')
    shrink = io.open('tmp/merge_shrink_0824.txt', 'w', encoding='utf-8')
    shrink.write('# 再導出のほうが枠が少なかったエントリ＝**消さずに残した**。実ページを見て人が判断する。\n')
    datewarn = []
    added_total = 0
    rows = []

    for sid, tickets in sorted(got.items(), key=lambda x: int(x[0])):
        eid = int(sid)
        e = by.get(eid)
        if e is None:
            log.write('!! id=%d が index に無い\n' % eid)
            continue
        old = e.get('tickets') or []
        have = {slot_key(t) for t in old}
        # 🚨同じ枠が「links.pia から取れた版（url無し）」と「別URLから取れた版（url有り）」の
        #   2つ返ってくることがある（bundleと個別ページの両方に同じ券種が載っているため）。
        #   そのまま足すと画面にバッジが二重に出るので、slot_key で1つに畳む。
        #   残すのは url 無しのほう＝エントリの主URL（links.pia）で買えるという意味なので迷わせない。
        new = []
        for t in sorted(tickets, key=lambda x: 0 if not x.get('url') else 1):
            k = slot_key(t)
            if k in have:
                continue
            have.add(k)
            new.append(t)
        if len(tickets) < len(old):
            shrink.write('id%-5d %-30s 登録%d枠 / 再導出%d枠 | %s\n' % (
                eid, (e.get('artist') or '')[:30], len(old), len(tickets),
                (e.get('links') or {}).get('pia', '')))
        if not new:
            continue
        added_total += len(new)
        log.write('== id%-5d %s : 枠 %d → %d\n' % (eid, e.get('artist', ''), len(old), len(old) + len(new)))
        for t in new:
            log.write('   + %s | 〆%s | %s\n' % (t.get('type'), t.get('date'), t.get('url') or '-'))
        rows.append((eid, e.get('artist', ''), len(old), len(old) + len(new)))

        # 千秋楽より後ろの公演が足された枠に含まれていないか
        cur = e.get('date') or ''
        latest = max([d for t in new for d in show_dates(t.get('type'))], default=None)
        if latest and latest.isoformat() > cur:
            datewarn.append((eid, e.get('artist', ''), cur, latest.isoformat()))

        if APPLY:
            e['tickets'] = old + new
            e['verifiedAt'] = '2026-08-24'

    log.write('\n=== 枠が増えたエントリ %d件 / 追加した枠 %d ===\n' % (len(rows), added_total))
    for i, n, a, b in rows:
        log.write('  id%-5d %-36s %d→%d 枠\n' % (i, (n or '')[:36], a, b))
    if datewarn:
        log.write('\n=== 🚨登録の千秋楽より後ろの公演が入った %d件（date の更新を人が判断）===\n' % len(datewarn))
        for i, n, cur, new_d in datewarn:
            log.write('  id%-5d %-30s date=%s → 実際は %s まである\n' % (i, (n or '')[:30], cur, new_d))
    log.close()
    shrink.close()

    print('枠が増えたエントリ %d件 / 追加した枠 %d → tmp/merge_diff_0824.txt' % (len(rows), added_total))
    if datewarn:
        print('🚨 千秋楽が伸びる可能性 %d件（tmp/merge_diff_0824.txt の末尾）' % len(datewarn))

    if not APPLY:
        print('(--apply で書き込み)')
        return 0

    shutil.copyfile(PATH, PATH + '.bak_0824_merge')
    dumped = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl)
    io.open(PATH, 'w', encoding='utf-8', newline='').write(src[:m.start(2)] + dumped + src[m.end(2):])
    print('書き込み完了')
    return 0


if __name__ == '__main__':
    sys.exit(main())
