import json, re
PIA='https://t.pia.jp/pia/event/event.do?eventCd='

entries=json.load(open('tmp/theater2_raw.json',encoding='utf-8'))
# genre table + strip _genre
gt=[]
for e in entries:
    g=e.pop('_genre','engeki'); e['genre']='new'
    gt.append(f"{e['id']}\t{g}\t{e.get('name','')}")
open('tmp/genre_table_theater2.tsv','w',encoding='utf-8').write('\n'.join(gt)+'\n')

# new 940 (merge batch1 + 1023 legs) — 11 tickets
e940={
 "id":940,
 "artist":"春風亭一之輔 らくごDE全国ツアー VOL.14 ドッサりまわるぜ2026",
 "name":"らくごDE全国ツアー VOL.14 春風亭一之輔のドッサりまわるぜ2026",
 "date":"2026-09-12",
 "dateLabel":"2026年9月12日〜10月15日 全国ツアー（千葉・福岡・熊本・愛知・岩手・福井・長野・山形・秋田・福島）",
 "venue":"全国ツアー","prefecture":"全国","genre":"owarai","price":None,
 "links":{"rakuten":None,"lawson":None,"pia":PIA+"2616973","eplus":None},
 "tickets":[
   {"type":"一般発売（千葉 君津 9/12公演）6/20 10:00発売","startDate":"2026-06-20","date":"2026-06-20","url":PIA+"2616973"},
   {"type":"一般発売（福岡 9/20公演）6/20 10:00発売","startDate":"2026-06-20","date":"2026-06-20","url":PIA+"2608204"},
   {"type":"先行2次受付（熊本 9/21公演）〜6/21 23:59","date":"2026-06-21","url":PIA+"2621317"},
   {"type":"一般発売（千葉 市川 9/30公演）6/21 10:00発売","startDate":"2026-06-21","date":"2026-06-21","url":PIA+"2617186"},
   {"type":"一般発売（愛知 9/18公演）6/27 10:00発売","startDate":"2026-06-27","date":"2026-06-27","url":PIA+"2620474"},
   {"type":"一般発売（岩手 9/27公演）6/27 10:00発売","startDate":"2026-06-27","date":"2026-06-27","url":PIA+"2610059"},
   {"type":"一般発売（熊本 9/21公演）6/27 10:00発売","startDate":"2026-06-27","date":"2026-06-27","url":PIA+"2621317"},
   {"type":"一般発売（福井 9/23・長野 10/3公演）7/4 10:00発売","startDate":"2026-07-04","date":"2026-07-04","url":PIA+"2619999"},
   {"type":"一般発売（秋田 10/12公演）7/11 9:00発売","startDate":"2026-07-11","date":"2026-07-11","url":PIA+"2610059"},
   {"type":"一般発売（山形 10/11公演）7/18 9:00発売","startDate":"2026-07-18","date":"2026-07-18","url":PIA+"2610059"},
   {"type":"一般発売（福島 10/15公演）7/25 10:00発売","startDate":"2026-07-25","date":"2026-07-25","url":PIA+"2610059"}
 ],
 "verified":True,"verifiedAt":"2026-06-19"
}

def fmt(o,base=2):
    s=json.dumps(o,ensure_ascii=False,indent=2)
    return '\n'.join('  '+ln for ln in s.split('\n'))

src=open('index.html',encoding='utf-8',newline='').read()
nl='\r\n' if '\r\n' in src else '\n'
text=src.replace('\r\n','\n')

# 1) replace 940
lines=text.split('\n')
pat=re.compile(r'^\s*"id":\s*940\s*,')
idx=next(i for i,l in enumerate(lines) if pat.match(l))
s=idx
while lines[s].strip()!='{': s-=1
oi=len(lines[s])-len(lines[s].lstrip())
en=idx
while en<len(lines):
    st=lines[en].strip(); ind=len(lines[en])-len(lines[en].lstrip())
    if st in('}','},') and ind==oi and en>s: break
    en+=1
had=lines[en].strip()=='},'
blk=fmt(e940).split('\n')
if had: blk[-1]+=','
lines[s:en+1]=blk
text='\n'.join(lines)

# 2) inject 48 entries at end of EVENTS array
i0=text.index('const EVENTS = ['); br=text.index('[',i0)
depth=0;i=br
while i<len(text):
    c=text[i]
    if c=='[':depth+=1
    elif c==']':
        depth-=1
        if depth==0:break
    i+=1
ci=i
block=',\n'.join(fmt(e) for e in entries)
head=text[:ci].rstrip(); tail=text[ci:]
text=head+',\n'+block+'\n'+tail

# 3) NEW_ORDER = injected ids
ids=[e['id'] for e in entries]
text=re.sub(r'const NEW_ORDER = \[[0-9,]*\];','const NEW_ORDER = ['+','.join(map(str,ids))+'];',text)

open('index.html','w',encoding='utf-8',newline='').write(text.replace('\n',nl))
print('940 merged (11 tickets) / injected',len(entries),'entries / NEW_ORDER',len(ids))
