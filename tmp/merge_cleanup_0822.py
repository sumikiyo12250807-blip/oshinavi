# -*- coding: utf-8 -*-
"""統合で作ってしまった「時刻違いの二重バッジ」を掃除する（2026-08-22）。

何が起きたか＝足すだけの統合をしたら、**古い枠の発売時刻が間違っていた**エントリで
同じ公演のバッジが2枚並んだ。例）PEDRO 茨城10/28
    古い枠: 一般発売（茨城 10/28公演）**8/22 10:00発売**   ← 登録時の誤り
    足した枠: 一般発売（茨城 10/28公演）**8/22 20:00発売** ← ぴあ実ページの正
reconcile が ❌QC-TIME で拾ってくれた（[[reference_reconcile_pia_qc_gate]]）。

直し方＝**時刻部分を落とすと文言が一致し、締切日も同じ**なら同じ枠なので、
   ぴあ由来（今回足した側）を残して古い方を落とす。ぴあが正（[[feedback_no_fake_info]]）。
   ⚠️時刻以外が違う枠は別物なので触らない。売り切れ枠(soldout/saleEnded)も触らない。
"""
import io
import json
import re
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')
APPLY = '--apply' in sys.argv

built = {e['id']: {(t['type'], t.get('date')) for t in e['tickets']}
         for e in json.load(open('tmp/merge_built_0822.json', encoding='utf-8'))}
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

TIME = re.compile(r'\d{1,2}:\d{2}')


def strip_time(s):
    return TIME.sub('', s or '')


log = io.open('tmp/merge_cleanup_0822.txt', 'w', encoding='utf-8')
dropped = 0
for e in EVENTS:
    b = built.get(e['id'])
    if not b:
        continue
    ts = e.get('tickets') or []
    from_pia = [t for t in ts if (t.get('type'), t.get('date')) in b]
    keys = {(strip_time(t['type']), t.get('date')) for t in from_pia}
    keep, drop = [], []
    for t in ts:
        if (t.get('type'), t.get('date')) in b:
            keep.append(t)
        elif t.get('soldout') or t.get('saleEnded'):
            keep.append(t)
        elif (strip_time(t.get('type')), t.get('date')) in keys:
            drop.append(t)
        else:
            keep.append(t)
    if drop:
        log.write('== id%-5d %s\n' % (e['id'], e.get('name', '')))
        for t in drop:
            same = [x['type'] for x in from_pia
                    if (strip_time(x['type']), x.get('date')) == (strip_time(t['type']), t.get('date'))]
            log.write('   - 落とす: %s\n     残す  : %s\n' % (t['type'], same[0] if same else '?'))
        dropped += len(drop)
        if APPLY:
            e['tickets'] = keep
log.write('\n=== 落とした枠 %d ===\n' % dropped)
log.close()
print('時刻違いの二重バッジ %d枠 → tmp/merge_cleanup_0822.txt' % dropped)

if APPLY:
    shutil.copyfile('index.html', 'index.html.bak_0822_cleanup')
    open('index.html', 'w', encoding='utf-8').write(
        h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2)
        + m.group(3) + h[m.end():])
    print('適用した')
else:
    print('（判定のみ。適用は --apply）')
