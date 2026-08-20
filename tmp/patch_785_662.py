# -*- coding: utf-8 -*-
import json, io, sys, shutil, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
txt = open('index.html', encoding='utf-8').read()
i = txt.index('const EVENTS = [') + len('const EVENTS = ')
arr, _ = json.JSONDecoder().raw_decode(txt, i)
byid = {e['id']: e for e in arr}

def tickets_block(tks):
    dumped = json.dumps(tks, ensure_ascii=False, indent=2)
    lines = dumped.split('\n')
    return lines[0] + '\n' + '\n'.join('    ' + l for l in lines[1:])

def replace_tickets(text, eid, newtks):
    e = byid[eid]
    key = f'\n    "id": {eid},\n'; si = text.find(key)
    m = re.search(r'\n  \},?\n', text[si:]); ei = si + m.end(); span = text[si:ei]
    old = '"tickets": ' + tickets_block(e['tickets'])
    assert span.count(old) == 1, (eid, span.count(old))
    return text[:si] + span.replace(old, '"tickets": ' + tickets_block(newtks)) + text[ei:]

new_txt = txt
# 785: 販売中化
new_txt = replace_tickets(new_txt, 785, [{
    'type': '一般発売（福岡 10/11・京都 12/12・石川 12/27・宮城 2/23・愛知 3/6・東京 5/14・大阪 5/23公演）〜5/22 23:59',
    'date': '2027-05-22'}])
# 785: pia URL fix
old_url = '"pia": "https://t.pia.jp/pia/ticketInformation.do?eventCd=2613017&rlsCd=001"'
new_url = '"pia": "https://t.pia.jp/pia/event/event.do?eventCd=2613017"'
assert new_txt.count(old_url) == 1
new_txt = new_txt.replace(old_url, new_url)
# 662: 大阪城のみ残す
new_txt = replace_tickets(new_txt, 662, [{
    'type': '一般発売（注釈・立見／大阪 7/11・7/12公演）〜7/2 23:59',
    'date': '2026-07-02',
    'url': 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2666393'}])
# 662: ev.date 6/20 -> 7/11
old662 = '\n    "id": 662,\n'
si = new_txt.find(old662); m = re.search(r'\n  \},?\n', new_txt[si:]); ei = si+m.end()
span = new_txt[si:ei]
assert span.count('"date": "2026-06-20"') == 1
span2 = span.replace('"date": "2026-06-20"', '"date": "2026-07-11"')
new_txt = new_txt[:si] + span2 + new_txt[ei:]

shutil.copy('index.html', 'index.html.bak_0621_785_662')
open('index.html', 'w', encoding='utf-8').write(new_txt)
print('OK patched 785 & 662 (backup index.html.bak_0621_785_662)')
