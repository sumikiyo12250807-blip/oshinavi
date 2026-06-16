# -*- coding: utf-8 -*-
"""同URL＋同販売日のバッジを1つに統合（県名＋公演日は列挙して保持）。対象7件。"""
import re, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def sell(t,d,u=None):
    o={"type":t,"date":d}
    if u: o["url"]=u
    return o
def pre(t,sd,u=None):
    o={"type":t,"startDate":sd,"date":sd}
    if u: o["url"]=u
    return o
TI=lambda cd:"https://t.pia.jp/pia/event/event.do?eventCd=%s"%cd  # not used
def tinfo(cd): return "https://t.pia.jp/pia/ticketInformation.do?eventCd=%s&rlsCd=001"%cd

FIX={}
FIX[785]=[pre("一般発売（福岡 10/11・京都 12/12・石川 12/27・宮城 2/23・愛知 3/6・東京 5/14・大阪 5/23公演）6/20 10:00発売","2026-06-20")]
FIX[838]=[pre("一般発売（茨城 11/11・埼玉 11/17・三重 11/19・岐阜 11/20・埼玉 11/25公演）6/25 10:00発売","2026-06-25")]
FIX[805]=[pre("一般発売（兵庫 9/23・宮城 10/4・大阪 10/31公演）7/11 10:00発売","2026-07-11")]
FIX[824]=[
 sell("一般発売（沖縄 7/11公演）〜6/25 23:59","2026-06-25"),
 pre("一般発売（北海道 9/4・9/6・広島 10/31公演）7/4 10:00発売","2026-07-04"),
 sell("一般発売（福島 9/25公演）〜9/9 23:59","2026-09-09"),
]
FIX[833]=[
 sell("一般発売（愛知 7/8公演）〜7/7 23:59","2026-07-07"),
 sell("一般発売（愛知 7/30公演）〜7/21 23:59","2026-07-21"),
 sell("一般発売（愛知 8/12公演）〜8/11 23:59","2026-08-11"),
 sell("オフィシャル2次先行（愛知 8/4・8/27・10/23公演）〜6/28 23:59","2026-06-28"),
 pre("一般発売（愛知 9/17公演）7/4 10:00発売","2026-07-04"),
 pre("一般発売（愛知 10/23公演）8/1 10:00発売","2026-08-01"),
]
FIX[851]=[
 sell("一般発売（茨城 6/19公演）〜6/18 23:59","2026-06-18"),
 sell("一般発売（福島 6/27公演）〜6/26 23:59","2026-06-26"),
 pre("一般発売（大阪 9/6・東京 9/23公演）6/27 10:00発売","2026-06-27"),
 sell("4次プレリザーブ（愛知 9/18公演）〜6/17 11:00","2026-06-17"),
]
# 763は会場別URLが違うのでレッグごとに統合（各レッグ内は同URL同販売日6/20）
FIX[763]=[
 pre("一般発売（山口 8/8・広島 9/5・岡山 9/6・島根 10/12公演）6/20 10:00発売","2026-06-20",tinfo("2622037")),
 pre("一般発売（石川 8/22・富山 11/8公演）6/20 10:00発売","2026-06-20",tinfo("2621691")),
 pre("一般発売（新潟 8/23・長野 11/7公演）6/20 10:00発売","2026-06-20",tinfo("2621692")),
]

src=open('index.html',encoding='utf-8').read()
def block(ts):
    items=[]
    for t in ts:
        keys=['type','startDate','date','url']; pres=[k for k in keys if k in t]
        L=['      {']
        for j,k in enumerate(pres):
            c=',' if j<len(pres)-1 else ''
            L.append('        %s: %s%s'%(json.dumps(k,ensure_ascii=False),json.dumps(t[k],ensure_ascii=False),c))
        L.append('      }')
        items.append('\n'.join(L))
    return '    "tickets": [\n'+',\n'.join(items)+'\n    ],'
for eid,ts in FIX.items():
    pat=re.compile(r'("id": %d,.*?)(    "tickets": \[\n.*?\n    \],)'%eid, re.S)
    src,n=pat.subn(lambda mm: mm.group(1)+block(ts), src, count=1)
    assert n==1, 'id%d=%d'%(eid,n)
open('index.html','w',encoding='utf-8').write(src)
print("統合完了:", sorted(FIX.keys()))
