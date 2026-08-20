# -*- coding: utf-8 -*-
import re, json, sys, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')

P='https://t.pia.jp/pia/event/event.do?eventCd='
def t(type_,date,startDate=None,url=None):
    d={'type':type_}
    if startDate: d['startDate']=startDate
    d['date']=date
    if url: d['url']=url
    return d

conv={
348:[t('一般発売（島根 7/4公演）〜7/2 23:59','2026-07-02')],
413:[t('一般発売（福岡 8/27公演）7/4 10:00発売','2026-07-04','2026-07-04')],
533:[t('一般発売（広島 8/30公演）〜8/20 23:59','2026-08-20')],
617:[t('一般発売（大分 9/12公演）〜9/11 23:59','2026-09-11',url=P+'2615930'),
     t('一般発売（宮崎 9/13公演）〜9/12 23:59','2026-09-12',url=P+'2615977'),
     t('一般発売（神奈川 10/11公演）〜10/10 23:59','2026-10-10',url=P+'2620866')],
692:[t('一般発売（愛知 10/25公演）〜10/24 23:59','2026-10-24')],
763:[t('一般発売（山口 8/8・広島 9/5・岡山 9/6・島根 10/12公演）〜10/11 23:59','2026-10-11',url='https://t.pia.jp/pia/ticketInformation.do?eventCd=2622037&rlsCd=001'),
     t('一般発売（石川 8/22・富山 11/8公演）〜11/7 23:59','2026-11-07',url='https://t.pia.jp/pia/ticketInformation.do?eventCd=2621691&rlsCd=001'),
     t('一般発売（新潟 8/23・長野 11/7公演）〜11/6 23:59','2026-11-06',url='https://t.pia.jp/pia/ticketInformation.do?eventCd=2621692&rlsCd=001')],
832:[t('一般発売（北海道 8/29公演）〜8/28 23:59','2026-08-28')],
846:[t('一般発売（埼玉 9/5公演）〜9/4 23:59','2026-09-04')],
875:[t('一般発売（宮城 10/16公演）〜10/13 23:59','2026-10-13')],
921:[t('一般発売（京都 9/25・9/26公演）〜9/23 23:59','2026-09-23')],
927:[t('一般発売（東京 9/26公演）〜9/21 23:59','2026-09-21')],
979:[t('一般発売（福岡 8/20〜8/24公演）〜8/11 23:59','2026-08-11')],
980:[t('一般発売（愛知 8/15・8/16公演）〜8/13 23:59','2026-08-13')],
983:[t('一般発売（兵庫 9/25公演）〜9/24 23:59','2026-09-24')],
984:[t('一般発売（東京 10/4公演）〜10/3 23:59','2026-10-03')],
985:[t('一般発売（東京 9/22公演）〜9/21 23:59','2026-09-21')],
986:[t('一般発売（兵庫 10/3・10/4公演）〜10/3 23:59','2026-10-03')],
987:[t('一般発売（宮崎 10/20公演）〜10/15 23:59','2026-10-15',url=P+'2619958'),
     t('一般発売（宮崎 10/21公演）〜10/19 23:59','2026-10-19',url=P+'2619959'),
     t('一般発売（宮崎 10/22公演）〜10/20 23:59','2026-10-20',url=P+'2619960'),
     t('一般発売（大分 10/23公演）〜10/21 23:59','2026-10-21',url=P+'2619961')],
989:[t('一般発売（東京 9/15公演）〜9/14 23:59','2026-09-14')],
990:[t('一般発売（東京 8/29公演）〜8/28 23:59','2026-08-28')],
991:[t('一般発売（東京 8/29公演）〜8/28 23:59','2026-08-28')],
992:[t('一般発売（東京 8/16〜8/31公演）〜8/27 23:59','2026-08-27',url='https://t.pia.jp/pia/event/event.do?eventBundleCd=b2669038'),
     t('一般発売（東京 9/2〜9/30公演）〜9/27 23:59','2026-09-27',url='https://t.pia.jp/pia/event/event.do?eventBundleCd=b2669039'),
     t('一般発売（東京 10/1〜10/31公演）〜10/28 23:59','2026-10-28',url='https://t.pia.jp/pia/event/event.do?eventBundleCd=b2669040'),
     t('一般発売（東京 11/1〜11/29公演）〜11/26 23:59','2026-11-26',url='https://t.pia.jp/pia/event/event.do?eventBundleCd=b2669041'),
     t('一般発売（東京 12/1〜12/27公演）〜12/24 23:59','2026-12-24',url='https://t.pia.jp/pia/event/event.do?eventBundleCd=b2669042')],
997:[t('一般発売（愛知 8/30公演）〜8/29 23:59','2026-08-29')],
998:[t('一般発売（兵庫 11/10・11/11公演）〜11/10 23:59','2026-11-10')],
999:[t('一般発売（東京・京都 8/6〜8/23公演）〜8/22 23:59','2026-08-22')],
1000:[t('一般発売（東京 8/8公演）〜7/30 23:59','2026-07-30')],
}

text=open('index.html',encoding='utf-8').read()

def serialize(tks):
    # 8-space field indent, 6-space item brace
    lines=['      ['  ] if False else None
    out='[\n'
    for j,tk in enumerate(tks):
        out+='      {\n'
        keys=list(tk.keys())
        for k in keys:
            v=tk[k]
            comma=',' if k!=keys[-1] else ''
            out+=f'        {json.dumps(k,ensure_ascii=False)}: {json.dumps(v,ensure_ascii=False)}{comma}\n'
        out+='      }'+(',' if j!=len(tks)-1 else '')+'\n'
    out+='    ]'
    return out

count=0
for eid,tks in conv.items():
    # locate entry
    m=re.search(r'"id": '+str(eid)+r',', text)
    if not m: print('NOTFOUND',eid); continue
    # find tickets array start after id
    ti=text.find('"tickets": [', m.end())
    if ti<0: print('NO TICKETS',eid); continue
    # find matching ]
    bs=text.find('[',ti)
    depth=0;i=bs
    while i<len(text):
        c=text[i]
        if c=='[':depth+=1
        elif c==']':
            depth-=1
            if depth==0:break
        i+=1
    new=serialize(tks)
    text=text[:ti]+'"tickets": '+new+text[i+1:]
    count+=1

open('index.html','w',encoding='utf-8').write(text)
print('converted',count,'entries')
