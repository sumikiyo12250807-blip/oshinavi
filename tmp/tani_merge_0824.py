# -*- coding: utf-8 -*-
"""谷山浩子の3公演を1エントリにまとめる（2026-08-24 ユーザー指示「ツアーはまとめて」）。

既存が愛知10/2(id3575)と宮城11/11(id4497)に割れていて、そこへ東京12/18が新規で出てきた。
ツアーは1エントリ（feedback_tour_consolidate）。id の小さい 3575 に寄せ、4497 は欠番にする。

枠・date・venue・prefecture・dateLabel は、3つのURLから build_pia_entries で再導出した結果を使う。

使い方: python tmp/tani_merge_0824.py [--apply]
"""
import io
import json
import re
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')

APPLY = '--apply' in sys.argv
PATH = 'index.html'
KEEP, DROP = 3575, 4497


def main():
    built = {e['id']: e for e in json.load(io.open('tmp/_tani_out.json', encoding='utf-8'))}
    b = built[700001]
    src = io.open(PATH, encoding='utf-8', newline='').read()
    nl = '\r\n' if '\r\n' in src else '\n'
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
    events = json.loads(m.group(2))
    by = {e['id']: e for e in events}

    keep, drop = by[KEEP], by[DROP]
    print('残す  id=%d %s date=%s 枠%d genre=%s' % (
        KEEP, keep.get('artist'), keep.get('date'), len(keep.get('tickets') or []), keep.get('genre')))
    print('畳む  id=%d %s date=%s 枠%d genre=%s' % (
        DROP, drop.get('artist'), drop.get('date'), len(drop.get('tickets') or []), drop.get('genre')))
    print('→ date=%s / venue=%s / pref=%s / 枠%d' % (
        b.get('date'), b.get('venue'), b.get('prefecture'), len(b.get('tickets') or [])))
    for t in b.get('tickets') or []:
        print('   - %s | 〆%s' % (t.get('type'), t.get('date')))

    if not APPLY:
        print('\n(--apply で書き込み)')
        return 0

    keep['tickets'] = b['tickets']
    for f in ('date', 'dateLabel', 'venue', 'prefecture'):
        if b.get(f):
            keep[f] = b[f]
    keep['verifiedAt'] = '2026-08-24'
    events = [e for e in events if e['id'] != DROP]

    shutil.copyfile(PATH, PATH + '.bak_0824_tani')
    dumped = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl)
    io.open(PATH, 'w', encoding='utf-8', newline='').write(src[:m.start(2)] + dumped + src[m.end(2):])
    print('\n書き込み完了（id%d を畳んで欠番に）' % DROP)
    return 0


if __name__ == '__main__':
    sys.exit(main())
