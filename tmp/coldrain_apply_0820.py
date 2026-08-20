# -*- coding: utf-8 -*-
"""coldrain の統合を適用する。
 ・4537 の tickets を作り直した7枠に差し替える（北海道10/21のプレリザーブが増える）
 ・venue / prefecture / date（千秋楽12/9）は**既存を保持**する
   ＝buildの出力は「今買える枠のある会場」だけになり、ツアー全体の会場が落ちるため
 ・宮城11/29の2枠には、単独エントリだった4185のぴあURL（eventCd=2626313）を付ける
 ・4185 は重複なので削除（別スクリプト）
"""
import io, json, re, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

SENDAI = "https://t.pia.jp/pia/event/event.do?eventCd=2626313"
built = json.load(io.open('tmp/built_coldrain.json', encoding='utf-8'))[0]
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

for e in EVENTS:
    if e['id'] != 4537:
        continue
    ts = [dict(t) for t in built['tickets']]
    for t in ts:
        if '宮城' in (t.get('type') or '') and not t.get('url'):
            t['url'] = SENDAI
    print('before 枠%d / venue %d会場 / date %s' % (
        len(e.get('tickets') or []), (e.get('venue') or '').count('／') + 1, e.get('date')))
    e['tickets'] = ts
    print('after  枠%d（venue・千秋楽は据え置き）' % len(ts))
    for t in ts:
        print('   -', t['type'], '| url=', (t.get('url') or '')[:60])

shutil.copyfile('index.html', 'index.html.bak_0820_coldrain')
open('index.html', 'w', encoding='utf-8').write(
    h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
print('=== 更新 ===')
