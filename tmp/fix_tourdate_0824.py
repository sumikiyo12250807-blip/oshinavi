# -*- coding: utf-8 -*-
"""統合で公演が増えた3件の「千秋楽・会場・都道府県」を取り直す（2026-08-24）。

統合は枠を足すだけにしてあるので、date（千秋楽）と venue が古いままになる。
放置すると期限切れ判定が誤爆する（今朝 id=1006 喜楽館で踏んだ型）。

date/venue/dateLabel/prefecture は build_pia_entries に全URLをまとめて渡した結果を使う。
（ticket.url が落ちる罠は tickets を使わないので無関係）

使い方: python tmp/fix_tourdate_0824.py [--apply]
"""
import io
import json
import re
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

APPLY = '--apply' in sys.argv
PATH = 'index.html'
IDS = [824, 876, 1634]


def main():
    plans = {p['id']: p for p in json.load(io.open('tmp/merge_plan_0824.json', encoding='utf-8'))}
    src = io.open(PATH, encoding='utf-8', newline='').read()
    nl = '\r\n' if '\r\n' in src else '\n'
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
    events = json.loads(m.group(2))
    by = {e['id']: e for e in events}

    cand = []
    for eid in IDS:
        cand.append({'newid': 800000 + eid, 'artist': by[eid].get('artist') or '',
                     'urls': plans[eid]['urls']})
    io.open('tmp/_tourdate.json', 'w', encoding='utf-8').write(json.dumps(cand, ensure_ascii=False))
    r = subprocess.run([sys.executable, 'tools/build_pia_entries.py', 'tmp/_tourdate.json'],
                       capture_output=True)
    if r.returncode != 0:
        print('取得失敗'); return 1
    built = {b['id'] - 800000: b for b in json.loads(r.stdout.decode('utf-8'))}

    for eid in IDS:
        e, b = by[eid], built.get(eid)
        if not b:
            print('!! id=%d 取得できず' % eid); continue
        print('id=%-5d %s' % (eid, e.get('artist')))
        print('   date  %s -> %s' % (e.get('date'), b.get('date')))
        print('   venue %s' % e.get('venue'))
        print('      -> %s' % b.get('venue'))
        print('   pref  %s -> %s' % (e.get('prefecture'), b.get('prefecture')))
        if APPLY and b.get('date') and b['date'] > (e.get('date') or ''):
            e['date'] = b['date']
            for f in ('dateLabel', 'venue', 'prefecture'):
                if b.get(f):
                    e[f] = b[f]
            e['verifiedAt'] = '2026-08-24'

    if not APPLY:
        print('\n(--apply で書き込み)')
        return 0
    shutil.copyfile(PATH, PATH + '.bak_0824_tourdate')
    dumped = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl)
    io.open(PATH, 'w', encoding='utf-8', newline='').write(src[:m.start(2)] + dumped + src[m.end(2):])
    print('\n書き込み完了')
    return 0


if __name__ == '__main__':
    sys.exit(main())
