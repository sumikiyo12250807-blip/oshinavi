# -*- coding: utf-8 -*-
"""3526 dustbox（豊洲PIT 10/10-10/11）は、ぴあが券種ごとに別ページを持っていた。
  eventCd=2629992 ＝ 1日券      （既存の登録がこちら）
  eventCd=2629991 ＝ 2日通し券   （今日の収集で見つかった・未登録）
文言が同じだと画面で区別できないので券種名を入れ、枠ごとに飛び先URLを付ける。
根拠＝両ページの生HTMLに「１日券」「通し」の記載を機械確認済み。
"""
import json, re, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

ONEDAY = "https://t.pia.jp/pia/event/event.do?eventCd=2629992"
TWODAY = "https://t.pia.jp/pia/event/event.do?eventCd=2629991"

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

for e in EVENTS:
    if e['id'] != 3526:
        continue
    ts = e.get('tickets') or []
    print('before:', [t['type'] for t in ts])
    for t in ts:
        if '【' not in t['type']:
            t['type'] = t['type'].replace('一般発売（', '一般発売【1日券】（')
            t['url'] = ONEDAY
    base = dict(ts[0])
    base['type'] = ts[0]['type'].replace('【1日券】', '【2日通し券】')
    base['url'] = TWODAY
    ts.append(base)
    e['tickets'] = ts
    print('after :', [t['type'] for t in ts])

shutil.copyfile('index.html', 'index.html.bak_0820_dustbox')
open('index.html', 'w', encoding='utf-8').write(
    h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
print('=== 更新 ===')
