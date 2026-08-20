# -*- coding: utf-8 -*-
import json, io, sys, shutil, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
tks = json.load(open('tmp/or21_tickets.json', encoding='utf-8'))
# 複合県の補完
for t in tks:
    if t['type'].startswith('先行（ファミマ）（ 11/27'):
        t['type'] = t['type'].replace('（ 11/27', '（香川・高知 11/27')
    if t['type'].startswith('プレリザーブ（ 10/31'):
        t['type'] = t['type'].replace('（ 10/31', '（鳥取・山口 10/31')

txt = open('index.html', encoding='utf-8').read()
i = txt.index('const EVENTS = [') + len('const EVENTS = ')
arr, _ = json.JSONDecoder().raw_decode(txt, i)
byid = {e['id']: e for e in arr}
e = byid[21]
def tickets_block(t):
    d = json.dumps(t, ensure_ascii=False, indent=2); l = d.split('\n')
    return l[0] + '\n' + '\n'.join('    ' + x for x in l[1:])
key = '\n    "id": 21,\n'; si = txt.find(key)
m = re.search(r'\n  \},?\n', txt[si:]); ei = si + m.end(); span = txt[si:ei]
# tickets
old_t = '"tickets": ' + tickets_block(e['tickets'])
assert span.count(old_t) == 1, span.count(old_t)
span = span.replace(old_t, '"tickets": ' + tickets_block(tks))
# meta scalars
reps = [
 ('"name": "ORANGE RANGE LIVE TOUR 026-027（結成25周年ホールツアー）"',
  '"name": "ORANGE RANGE LIVE TOUR 2026-2027（結成25周年ホールツアー）"'),
 ('"date": "2027-02-21"', '"date": "2027-03-07"'),
 ('"dateLabel": "2027年1月9日(土)東京／2月21日(日)愛知"',
  '"dateLabel": "2026年8月〜2027年3月 全国ツアー"'),
 ('"venue": "NHKホール／フォレストホール"', '"venue": "全国ツアー"'),
 ('"prefecture": "東京・愛知"', '"prefecture": "全国"'),
]
for a,b in reps:
    assert span.count(a)==1, ('miss',a,span.count(a))
    span = span.replace(a,b)
new_txt = txt[:si] + span + txt[ei:]
shutil.copy('index.html','index.html.bak_0621_or21_rebuild')
open('index.html','w',encoding='utf-8').write(new_txt)
print('OK rebuilt id21 (11枠・全国ツアー化)')
for t in tks: print('  ',t['type'])
