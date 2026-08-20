# -*- coding: utf-8 -*-
"""tmp/theater_final.json の54件を genre:"new" で index.html EVENTS末尾に投入。
NEW_ORDER を投入id昇順で更新。"""
import json, io, sys, shutil, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
new_entries = json.load(open('tmp/theater_final.json', encoding='utf-8'))
txt = open('index.html', encoding='utf-8').read()
i = txt.index('const EVENTS = [') + len('const EVENTS = ')
arr, endpos = json.JSONDecoder().raw_decode(txt, i)
before_ids = {e['id'] for e in arr}
for e in new_entries:
    assert e['id'] not in before_ids, ('id collision', e['id'])

def ser(e):
    body = json.dumps(e, ensure_ascii=False, indent=2)
    return '\n'.join('  ' + ln for ln in body.split('\n'))
entries_text = ',\n'.join(ser(e) for e in new_entries)

bracket = endpos - 1
assert txt[bracket] == ']', txt[bracket-3:bracket+3]
before = txt[:bracket].rstrip()
after = txt[bracket:]
new_txt = before + ',\n' + entries_text + '\n' + after

new_ids = sorted(e['id'] for e in new_entries)
no = '[' + ', '.join(str(x) for x in new_ids) + ']'
new_txt, n = re.subn(r'(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]', r'\g<1>' + no, new_txt, count=1)
assert n == 1, 'NEW_ORDER replace=%d' % n

i2 = new_txt.index('const EVENTS = [') + len('const EVENTS = ')
arr2, _ = json.JSONDecoder().raw_decode(new_txt, i2)
assert len(arr2) == len(arr) + len(new_entries), (len(arr2), len(arr), len(new_entries))

shutil.copy('index.html', 'index.html.bak_0621_theater_new')
open('index.html', 'w', encoding='utf-8').write(new_txt)
print('投入', len(new_entries), '件 id', new_ids[0], '..', new_ids[-1])
print('EVENTS', len(arr), '→', len(arr2), '件 / NEW_ORDER', len(new_ids), '件')
