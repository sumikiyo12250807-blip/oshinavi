# -*- coding: utf-8 -*-
"""tmp/eplus_fix_0817.json をもとに、e+由来の「M/D HH:MM発売」型 type を
「〜M/D HH:MM」（締切）形に直し、役目を終えた startDate を落とす。

🚨 CRLF保持のためバイナリで読み書きし、JSONは作り直さない（対象のticketオブジェクトだけ文字列置換）。
   [[feedback_index_html_crlf_preserve]]
"""
import re, json, io, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

APPLY = '--apply' in sys.argv
data = json.load(io.open('tmp/eplus_fix_0817.json', encoding='utf-8'))

blob = open('index.html', 'rb').read()
text = blob.decode('utf-8')
before_crlf = text.count('\r\n')

# エントリ境界（"id": N, の位置）
id_pos = {}
for m in re.finditer(r'\n\s*"id": (\d+),', text):
    id_pos.setdefault(int(m.group(1)), m.start())
ordered = sorted(id_pos.items(), key=lambda kv: kv[1])


def entry_span(eid):
    for i, (k, p) in enumerate(ordered):
        if k == eid:
            end = ordered[i + 1][1] if i + 1 < len(ordered) else len(text)
            return p, end
    return None


def md(iso):
    y, m, d = iso.split('-')
    return '%d/%d' % (int(m), int(d))


changed, skipped = 0, []
for o in data:
    pick = o.get('pick')
    if not pick or pick['ed'] != o['date']:
        skipped.append((o['id'], o['type'], 'e+の終了日が登録と違う/窓なし'))
        continue
    new_type = re.sub(r'\d{1,2}/\d{1,2}\s*\d{1,2}:\d{2}\s*(発売|販売開始|受付開始)\s*$',
                      '〜%s %s' % (md(pick['ed']), pick['ed_time']), o['type'])
    if new_type == o['type']:
        skipped.append((o['id'], o['type'], 'type書き換え不発'))
        continue
    span = entry_span(o['id'])
    if not span:
        skipped.append((o['id'], o['type'], 'エントリが見つからない'))
        continue
    s, e = span
    seg = text[s:e]
    # 対象ticketオブジェクト（"type": 旧 を含む {...}）を1つだけ切り出す
    m = re.search(r'\{[^{}]*?"type": "%s"[^{}]*?\}' % re.escape(o['type']), seg, re.S)
    if not m:
        skipped.append((o['id'], o['type'], 'ticketブロックが見つからない'))
        continue
    obj = m.group(0)
    new_obj = obj.replace('"type": "%s"' % o['type'], '"type": "%s"' % new_type)
    # startDate 行を丸ごと落とす（発売は済んでいる＝もう発売日は要らない）
    new_obj2 = re.sub(r'\r?\n\s*"startDate": "[^"]*",', '', new_obj)
    if new_obj2 == new_obj:
        new_obj2 = re.sub(r',\r?\n\s*"startDate": "[^"]*"', '', new_obj)
    seg2 = seg[:m.start()] + new_obj2 + seg[m.end():]
    text = text[:s] + seg2 + text[e:]
    # 位置がずれるので都度作り直す
    id_pos = {}
    for mm in re.finditer(r'\n\s*"id": (\d+),', text):
        id_pos.setdefault(int(mm.group(1)), mm.start())
    ordered = sorted(id_pos.items(), key=lambda kv: kv[1])
    changed += 1
    print('id%-5s %s\n      → %s' % (o['id'], o['type'], new_type))

after_crlf = text.count('\r\n')
print('\n書き換え %d枠 / 見送り %d枠' % (changed, len(skipped)))
for eid, ty, why in skipped:
    print('  見送り id%s %s（%s）' % (eid, ty[:40], why))
print('CRLF: %d → %d' % (before_crlf, after_crlf))

if APPLY:
    bak = 'index.html.bak_0817_eplus_time'
    open(bak, 'wb').write(blob)
    open('index.html', 'wb').write(text.encode('utf-8'))
    print('適用しました（backup: %s）' % bak)
else:
    print('（判定のみ。適用するなら --apply）')
