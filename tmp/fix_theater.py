import re, json

PIA='https://t.pia.jp/pia/event/event.do?eventCd='
BUN='https://t.pia.jp/pia/event/event.do?eventBundleCd='

# new/replacement entry objects
rebuild = {
940: {
 "id":940,
 "artist":"春風亭一之輔 らくごDE全国ツアー VOL.14 ドッサりまわるぜ2026",
 "name":"らくごDE全国ツアー VOL.14 春風亭一之輔のドッサりまわるぜ2026",
 "date":"2026-09-12",
 "dateLabel":"2026年9月12日〜9月30日 全国ツアー（千葉・福岡・熊本）",
 "venue":"全国ツアー（君津市民文化ホール／市川市文化会館／福岡国際会議場／熊本県立劇場）",
 "prefecture":"全国","genre":"new","price":None,
 "links":{"rakuten":None,"lawson":None,"pia":PIA+"2616973","eplus":None},
 "tickets":[
   {"type":"一般発売（千葉 君津 9/12公演）6/20 10:00発売","startDate":"2026-06-20","date":"2026-06-20","url":PIA+"2616973"},
   {"type":"一般発売（福岡 9/20公演）6/20 10:00発売","startDate":"2026-06-20","date":"2026-06-20","url":PIA+"2608204"},
   {"type":"先行2次受付（熊本 9/21公演）〜6/21 23:59","date":"2026-06-21","url":PIA+"2621317"},
   {"type":"一般発売（千葉 市川 9/30公演）6/21 10:00発売","startDate":"2026-06-21","date":"2026-06-21","url":PIA+"2617186"},
   {"type":"一般発売（熊本 9/21公演）6/27 10:00発売","startDate":"2026-06-27","date":"2026-06-27","url":PIA+"2621317"}
 ],
 "verified":True,"verifiedAt":"2026-06-19"
},
942: {
 "id":942,
 "artist":"キーウ・クラシック・バレエ",
 "name":"キーウ・クラシック・バレエ 2026 全国ツアー",
 "date":"2026-10-31",
 "dateLabel":"2026年10月31日〜12月25日 全国ツアー（茨城・埼玉・静岡・神奈川・愛知・兵庫・大分・東京・大阪・福井・宮城・栃木・千葉・広島・島根 ほか）",
 "venue":"全国ツアー","prefecture":"全国","genre":"new","price":None,
 "links":{"rakuten":None,"lawson":None,"pia":BUN+"b2667971","eplus":None},
 "tickets":[
   {"type":"一般発売（島根 11/28公演）6/20 10:00発売","startDate":"2026-06-20","date":"2026-06-20"},
   {"type":"4次プリセール（東京 練馬 12/13公演）〜6/27 23:59","date":"2026-06-27"},
   {"type":"一般発売（茨城 10/31公演）〜10/28 23:59","date":"2026-10-28"},
   {"type":"一般発売（埼玉 越谷 11/1公演）〜10/29 23:59","date":"2026-10-29"},
   {"type":"一般発売（静岡 三島 11/5公演）〜11/1 23:59","date":"2026-11-01"},
   {"type":"一般発売（神奈川 茅ヶ崎 11/6公演）〜11/3 23:59","date":"2026-11-03"},
   {"type":"一般発売（愛知 知立 11/17公演）〜11/12 23:59","date":"2026-11-12"},
   {"type":"一般発売（兵庫 明石 11/20公演）〜11/17 23:59","date":"2026-11-17"},
   {"type":"一般発売（大分 11/30公演）〜11/26 23:59","date":"2026-11-26"},
   {"type":"一般発売（東京 調布 12/6公演）〜12/3 23:59","date":"2026-12-03"},
   {"type":"一般発売（大阪・福井・埼玉・東京 11/3〜12/22公演）〜12/17 23:59","date":"2026-12-17"},
   {"type":"一般発売（宮城・栃木・埼玉・千葉・東京・神奈川・静岡・広島 各公演）〜12/21 23:59","date":"2026-12-21"},
   {"type":"一般発売（兵庫 伊丹 12/25公演）〜12/22 23:59","date":"2026-12-22"}
 ],
 "verified":True,"verifiedAt":"2026-06-19"
},
966: {
 "id":966,
 "artist":"神戸新開地・喜楽館 8月【昼席】",
 "name":"神戸新開地・喜楽館 ８月【昼席】",
 "date":"2026-08-01",
 "dateLabel":"2026年8月1日〜8月23日 兵庫 神戸新開地・喜楽館【昼席】",
 "venue":"神戸新開地・喜楽館","prefecture":"兵庫","genre":"new","price":None,
 "links":{"rakuten":None,"lawson":None,"pia":PIA+"2620437","eplus":None},
 "tickets":[
   {"type":"一般発売（兵庫 8/1〜2昼席）〜8/1 23:59","date":"2026-08-01"},
   {"type":"一般発売（兵庫 8/3〜9昼席）〜8/8 23:59","date":"2026-08-08"},
   {"type":"一般発売（兵庫 8/10〜16昼席）〜8/15 23:59","date":"2026-08-15"},
   {"type":"一般発売（兵庫 8/17〜23昼席）6/20 12:00発売","startDate":"2026-06-20","date":"2026-06-20"}
 ],
 "verified":True,"verifiedAt":"2026-06-19"
},
}
delete_ids = {955, 981}

def fmt(e):
    s=json.dumps(e,ensure_ascii=False,indent=2)
    return '\n'.join('  '+ln for ln in s.split('\n'))

src=open('index.html',encoding='utf-8',newline='').read()
nl='\r\n' if '\r\n' in src else '\n'
text=src.replace('\r\n','\n')
lines=text.split('\n')

def find_span(lines, eid):
    pat=re.compile(r'^\s*"id":\s*'+str(eid)+r'\s*,')
    idx=next((i for i,l in enumerate(lines) if pat.match(l)),None)
    if idx is None: return None
    s=idx
    while s>=0 and lines[s].strip()!='{': s-=1
    oi=len(lines[s])-len(lines[s].lstrip())
    e=idx
    while e<len(lines):
        st=lines[e].strip(); ind=len(lines[e])-len(lines[e].lstrip())
        if st in('}','},') and ind==oi and e>s: break
        e+=1
    return s,e

# process deletes + rebuilds from bottom to top to keep indices
targets=[]
for eid in list(rebuild)+list(delete_ids):
    sp=find_span(lines,eid)
    if sp: targets.append((sp[0],sp[1],eid))
targets.sort(reverse=True)
for s,e,eid in targets:
    had_comma = lines[e].strip()=='},'
    if eid in delete_ids:
        # remove lines s..e ; also remove the comma artifact (if not last, line e was '},')
        del lines[s:e+1]
    else:
        block=fmt(rebuild[eid])
        block_lines=block.split('\n')
        if had_comma: block_lines[-1]=block_lines[-1]+','
        lines[s:e+1]=block_lines

text='\n'.join(lines)

# NEW_ORDER: remove deleted ids
m=re.search(r'const NEW_ORDER = \[([0-9,]*)\];',text)
ids=[int(x) for x in m.group(1).split(',') if x.strip()]
ids=[i for i in ids if i not in delete_ids]
text=re.sub(r'const NEW_ORDER = \[[0-9,]*\];','const NEW_ORDER = ['+','.join(map(str,ids))+'];',text)

open('index.html','w',encoding='utf-8',newline='').write(text.replace('\n',nl))
print("rebuilt:",sorted(rebuild),"deleted:",sorted(delete_ids))
print("NEW_ORDER count:",len(ids))
