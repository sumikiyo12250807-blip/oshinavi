# -*- coding: utf-8 -*-
"""県が空のTIGETエントリに、会場名・公演名の地名から県を入れ、バッジにも県を足す。

🚨1回目は re.sub の置換文字列で後方参照が壊れ、バッジの公演日が chr(1) になった。
   後方参照を使わず **lambda で組み立てる**（これなら壊れない）。
"""
import re, json, io, importlib.util

s = importlib.util.spec_from_file_location('th', 'tools/tiget_harvest.py')
th = importlib.util.module_from_spec(s)
s.loader.exec_module(th)

h = io.open('index.html', encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

WHEN = re.compile(r'（(\d{1,2}/\d{1,2}(?:\s\d{1,2}:\d{2})?公演)）')
o = io.open('tmp/fill_pref2_0918.txt', 'w', encoding='utf-8')
filled = stream = 0
skipped = []
for e in EVENTS:
    if 'tiget.net' not in json.dumps(e, ensure_ascii=False):
        continue
    if e.get('prefecture'):
        continue
    ven, nm = e.get('venue') or '', e.get('name') or ''
    if re.search(r'配信|オンライン|アーカイブ', ven + nm):
        stream += 1
        continue
    p = th.pref_from_place(ven) or th.pref_from_place(nm)
    if not p:
        skipped.append((e['id'], nm[:34], ven[:24]))
        continue
    e['prefecture'] = p
    n = 0
    for t in e['tickets']:
        t2 = WHEN.sub(lambda mm: '（%s %s）' % (p, mm.group(1)), t['type'])
        if t2 != t['type']:
            t['type'] = t2
            n += 1
    o.write('✅ id%d → %s ｜%s（%s）｜バッジ%d枠\n' % (e['id'], p, nm[:30], ven[:20], n))
    filled += 1

o.write('\n県を入れた %d件 / 配信で入れない %d件 / 決まらない %d件\n' % (filled, stream, len(skipped)))
for r in skipped[:40]:
    o.write('   ❓ id%s %s（%s）\n' % r)
o.close()

out = h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL) + m.group(3) + h[m.end():]
assert chr(1) not in out, '置換が壊れている（chr(1)が入った）'
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
