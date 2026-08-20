# -*- coding: utf-8 -*-
"""tour_tickets.json の9件を index.html に適用（span-scoped置換）。631/802は手当て。"""
import json, io, sys, shutil, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
tt = json.load(open('tmp/tour_tickets.json', encoding='utf-8'))
# 手当て
tt['631']['tickets'] = [{'type':'一般発売（北海道 9/5〜9/6公演）〜8/18 23:59','date':'2026-08-18'}]
for t in tt['802']['tickets']:
    if t['type'].startswith('一般発売（ 9/21'):
        t['type'] = '一般発売（富山 9/21・長野 9/22公演）〜9/21 23:59'

txt = open('index.html', encoding='utf-8').read()
i = txt.index('const EVENTS = [') + len('const EVENTS = ')
arr, _ = json.JSONDecoder().raw_decode(txt, i)
byid = {e['id']: e for e in arr}

def tickets_block(tks):
    dumped = json.dumps(tks, ensure_ascii=False, indent=2)
    lines = dumped.split('\n')
    return lines[0] + '\n' + '\n'.join('    ' + l for l in lines[1:])

new_txt = txt; applied=0; problems=[]
for eid_s, p in tt.items():
    eid=int(eid_s); e=byid[eid]
    key=f'\n    "id": {eid},\n'; si=new_txt.find(key)
    m=re.search(r'\n  \},?\n', new_txt[si:]); ei=si+m.end(); span=new_txt[si:ei]
    old_block='"tickets": '+tickets_block(e['tickets'])
    if span.count(old_block)!=1: problems.append((eid,span.count(old_block))); continue
    newtks=[{'type':t['type'],'date':t['date']} for t in p['tickets']]
    new_block='"tickets": '+tickets_block(newtks)
    new_txt=new_txt[:si]+span.replace(old_block,new_block)+new_txt[ei:]; applied+=1

print('applied',applied,'/',len(tt))
if problems: print('PROBLEM',problems)
else:
    shutil.copy('index.html','index.html.bak_0621_tours')
    open('index.html','w',encoding='utf-8').write(new_txt)
    print('WROTE index.html (backup index.html.bak_0621_tours)')
