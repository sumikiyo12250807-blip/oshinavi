# -*- coding: utf-8 -*-
"""round2検証で見つかった5件の漏れを補修（index.html内のtickets差替＋839はpref/dateLabelも）。"""
import re, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def sell(t,d): return {"type":t,"date":d}
def pre(t,sd): return {"type":t,"startDate":sd,"date":sd}

FIX={}
FIX[813]={"tickets":[
  sell("プレリザーブ（石川 8/15公演）〜6/22 11:00","2026-06-22"),
  pre("一般発売（石川 8/15公演）6/27 10:00発売","2026-06-27"),
]}
FIX[833]={"tickets":[
  sell("一般発売（愛知 7/8公演）〜7/7 23:59","2026-07-07"),
  sell("一般発売（愛知 7/30公演）〜7/21 23:59","2026-07-21"),
  sell("一般発売（愛知 8/12公演）〜8/11 23:59","2026-08-11"),
  sell("オフィシャル2次先行（愛知 8/4公演）〜6/28 23:59","2026-06-28"),
  sell("オフィシャル2次先行（愛知 8/27公演）〜6/28 23:59","2026-06-28"),
  pre("一般発売（愛知 9/17公演）7/4 10:00発売","2026-07-04"),
  pre("一般発売（愛知 10/23公演）8/1 10:00発売","2026-08-01"),
]}
FIX[836]={"tickets":[
  sell("一般発売（栃木 6/28公演）〜6/18 23:59","2026-06-18"),
  sell("一般発売（岡山 7/9公演）〜6/30 23:59","2026-06-30"),
  sell("一般発売（島根 7/11公演）〜7/2 23:59","2026-07-02"),
  sell("一般発売（京都 7/24公演）〜7/15 23:59","2026-07-15"),
  sell("一般発売（岩手 7/31公演）〜7/22 23:59","2026-07-22"),
  sell("一般発売（北海道 8/2公演）〜7/23 23:59","2026-07-23"),
  sell("一般発売（宮城 8/8公演）〜7/30 23:59","2026-07-30"),
  sell("一般発売（新潟 8/9公演）〜7/30 23:59","2026-07-30"),
  sell("一般発売（石川 8/11公演）〜7/30 23:59","2026-07-30"),
  sell("一般発売（福岡 8/15公演）〜8/14 23:59","2026-08-14"),
  sell("一般発売（広島 8/16公演）〜8/6 23:59","2026-08-06"),
  sell("一般発売（沖縄 10/4公演）〜10/3 23:59","2026-10-03"),
  sell("ファミマ先行（大阪・東京 9/4公演）〜6/30 23:59","2026-06-30"),
]}
FIX[839]={"prefecture":"京都・兵庫・広島・山口・佐賀・大分",
  "dateLabel":"2026年7月18日 京都ほか / 9月12日 佐賀 / 9月13日 大分",
  "tickets":[
  sell("一般発売（京都・兵庫・広島・山口公演）〜7/18 23:59","2026-07-18"),
  sell("プレリザーブ（佐賀 9/12・大分 9/13公演）〜6/21 23:59","2026-06-21"),
  pre("一般発売（佐賀 9/12・大分 9/13公演）7/4 10:00発売","2026-07-04"),
]}
FIX[845]={"tickets":[
  sell("先行（東京 10/15公演）〜6/24 23:59","2026-06-24"),
  pre("一般発売（東京 10/15公演）7/10 10:00発売","2026-07-10"),
]}

src=open('index.html',encoding='utf-8').read()
def block(tickets):
    items=[]
    for t in tickets:
        keys=['type','startDate','date','url']; pres=[k for k in keys if k in t]
        lines=['      {']
        for j,k in enumerate(pres):
            comma=',' if j<len(pres)-1 else ''
            lines.append('        %s: %s%s'%(json.dumps(k,ensure_ascii=False),json.dumps(t[k],ensure_ascii=False),comma))
        lines.append('      }')
        items.append('\n'.join(lines))
    return '    "tickets": [\n'+',\n'.join(items)+'\n    ],'

for eid,fx in FIX.items():
    # pref/dateLabel
    if 'prefecture' in fx:
        src=re.sub(r'("id": %d,(?:(?!"id":)[\s\S])*?"prefecture": )"[^"]*"'%eid, lambda mm: mm.group(1)+json.dumps(fx['prefecture'],ensure_ascii=False), src, count=1)
    if 'dateLabel' in fx:
        src=re.sub(r'("id": %d,(?:(?!"id":)[\s\S])*?"dateLabel": )"[^"]*"'%eid, lambda mm: mm.group(1)+json.dumps(fx['dateLabel'],ensure_ascii=False), src, count=1)
    pat=re.compile(r'("id": %d,.*?)(    "tickets": \[\n.*?\n    \],)'%eid, re.S)
    nb=block(fx['tickets'])
    src,n=pat.subn(lambda mm: mm.group(1)+nb, src, count=1)
    assert n==1, 'id%d tickets replace=%d'%(eid,n)
open('index.html','w',encoding='utf-8').write(src)
print('補修完了:', list(FIX.keys()))
