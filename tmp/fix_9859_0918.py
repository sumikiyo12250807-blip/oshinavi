# -*- coding: utf-8 -*-
# id9859 大阪フィル＝登録の「先行〜9/15 11:00」は締切が延びて「〜9/29 11:00」になっていた
# （ぴあ実ページ eventCd=2631900 は [抽選受付中] is-active）。同じ券種名なので差し替える。
import re, json, io

NEW = json.load(open('tmp/built_9859_0918.json', encoding='utf-8'))[0]['tickets']
h = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

hit = 0
for e in EVENTS:
    if e['id'] != 9859:
        continue
    old = e.get('tickets') or []
    # 売り切れ・販売終了の印が付いた枠は残す（表示に出ているので消さない）
    keep = [t for t in old if t.get('soldout') or t.get('saleEnded')]
    # 取り直した枠と同じ券種名（日付部分を落として比較）のものは置き換える
    def base(s):
        return re.sub(r'〜?\d{1,2}/\d{1,2}\s*\d{0,2}:?\d{0,2}.*$', '', s or '').strip()
    newbase = {base(t.get('type')) for t in NEW}
    keep += [t for t in old if not (t.get('soldout') or t.get('saleEnded'))
             and base(t.get('type')) not in newbase]
    e['tickets'] = list(NEW) + keep
    hit += 1

assert hit == 1, hit
open('index.html', 'w', encoding='utf-8', newline='').write(
    h[:m.start(2)] + json.dumps(EVENTS, ensure_ascii=False, indent=2) + h[m.end(2):])
o = io.open('tmp/fix_9859_0918.txt', 'w', encoding='utf-8')
for e in EVENTS:
    if e['id'] == 9859:
        for t in e['tickets']:
            o.write(f"{t.get('type','')} | date={t.get('date')} | sold={t.get('soldout')}\n")
o.close()
print('ok')
