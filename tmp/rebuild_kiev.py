import re, json
e = {
 "id":942,
 "artist":"キーウ・クラシック・バレエ",
 "name":"キーウ・クラシック・バレエ 2026 全国ツアー",
 "date":"2026-10-31",
 "dateLabel":"2026年10月31日〜12月25日 全国ツアー（島根・愛知・岐阜・東京・茨城・埼玉・静岡・神奈川・兵庫・大分・宮城・栃木・千葉・広島・大阪・福井 ほか）",
 "venue":"全国ツアー","prefecture":"全国","genre":"new","price":None,
 "links":{"rakuten":None,"lawson":None,"pia":"https://t.pia.jp/pia/event/event.do?eventBundleCd=b2667971","eplus":None},
 "tickets":[
   {"type":"一般発売（島根 11/28公演）6/20 10:00発売","startDate":"2026-06-20","date":"2026-06-20"},
   {"type":"一般発売（愛知 豊橋 11/13公演）6/21 10:00発売","startDate":"2026-06-21","date":"2026-06-21"},
   {"type":"プリセール（岐阜 長良川 11/18公演）6/25 10:00発売","startDate":"2026-06-25","date":"2026-06-25"},
   {"type":"4次プリセール（東京 練馬 12/13公演）〜6/27 23:59","date":"2026-06-27"},
   {"type":"一般発売（東京 練馬 12/13公演）6/28 10:00発売","startDate":"2026-06-28","date":"2026-06-28"},
   {"type":"一般発売（岐阜 長良川 11/18公演）7/14 10:00発売","startDate":"2026-07-14","date":"2026-07-14"},
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
}
def fmt(o):
    s=json.dumps(o,ensure_ascii=False,indent=2)
    return '\n'.join('  '+ln for ln in s.split('\n'))
src=open('index.html',encoding='utf-8',newline='').read()
nl='\r\n' if '\r\n' in src else '\n'
text=src.replace('\r\n','\n'); lines=text.split('\n')
pat=re.compile(r'^\s*"id":\s*942\s*,')
idx=next(i for i,l in enumerate(lines) if pat.match(l))
s=idx
while lines[s].strip()!='{': s-=1
oi=len(lines[s])-len(lines[s].lstrip())
en=idx
while en<len(lines):
    st=lines[en].strip(); ind=len(lines[en])-len(lines[en].lstrip())
    if st in('}','},') and ind==oi and en>s: break
    en+=1
had_comma=lines[en].strip()=='},'
block=fmt(e).split('\n')
if had_comma: block[-1]+=','
lines[s:en+1]=block
open('index.html','w',encoding='utf-8',newline='').write('\n'.join(lines).replace('\n',nl))
print("942 rebuilt with",len(e['tickets']),"tickets")
