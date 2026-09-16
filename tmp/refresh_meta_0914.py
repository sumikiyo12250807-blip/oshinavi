# -*- coding: utf-8 -*-
"""ヒールで枠（tickets）だけ入れ替えたエントリの、公演日・会期・会場・県をぴあから作り直す（2026-09-14）。
ヒールは tickets しか置き換えないので、終わった公演から次の公演へ中身が移った子（例 4307 レッドイーグルス
9/13 → 9/26・27）はカードの date が古いまま＝画面に出ない。build_pia_entries.build() で同じページを組み直し、
date / dateLabel / venue / prefecture だけを写す（tickets・genre・links は触らない）。
入れるのは「これから行われる公演」だけ（memory feedback_show_true_dates_not_sellable_range）＝build の出力がそれ。

使い方: python tmp/refresh_meta_0914.py <id,id,...> [--apply]
"""
import io
import json
import re
import sys

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import build_pia_entries as B  # noqa: E402

IDS = [int(x) for x in sys.argv[1].split(',') if x.strip()]
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
by = {e['id']: e for e in events}
changed = 0
for i in IDS:
    e = by[i]
    urls = [(e.get('links') or {}).get('pia')] + [t.get('url') for t in e.get('tickets') or []]
    urls = [u for u in dict.fromkeys(urls) if u and 'pia.jp' in u]
    b = B.build({'newid': i, 'artist': e.get('artist') or e.get('name'), 'urls': urls})
    if not b:
        print('id%s 組めなかった＝触らない' % i)
        continue
    print('id%s %s' % (i, (e.get('name') or '')[:40]))
    for k in ('date', 'dateLabel', 'venue', 'prefecture'):
        print('   %-10s %s → %s' % (k, e.get(k), b.get(k)))
        if e.get(k) != b.get(k):
            e[k] = b.get(k)
            changed += 1
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
body = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl)
io.open('index.html', 'w', encoding='utf-8', newline='').write(src[:m.start()] + m.group(1) + body + m.group(3) + src[m.end():])
print('書き込み完了（%d項目）' % changed)
