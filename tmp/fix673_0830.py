# -*- coding: utf-8 -*-
"""673 THE BACK HORN の千秋楽を実データに合わせて 8/29 → 9/4 LIQUIDROOM(東京) に伸ばす。
根拠＝ぴあ b2668655 の券種一覧に「2026-09-04 東京都 ＬＩＱＵＩＤＲＯＯＭ 一般発売＜９／４公演＞」がある。
枠は受付終了で買える枠0だが、公演が未来なので削除しない（枠には手を触れない）。"""
import io,re,json,sys,shutil
sys.stdout.reconfigure(encoding='utf-8')
P='index.html'
shutil.copy(P,'index.html.bak_0830_fix673')
src=io.open(P,encoding='utf-8',newline='').read()
m=re.search(r'(  const EVENTS = )(\[.*?\])(;)',src,re.S)
EVENTS=json.loads(m.group(2))
n=0
for e in EVENTS:
    if e['id']!=673: continue
    print('before:',e['date'],e.get('venue'),e.get('prefecture'))
    e['date']='2026-09-04'
    e['dateLabel']='2026年9月4日(金) 東京 LIQUIDROOM'
    e['venue']='LIQUIDROOM'
    e['prefecture']='東京'
    n+=1
    print('after :',e['date'],e.get('venue'),e.get('prefecture'))
assert n==1, n
arr=json.dumps(EVENTS,ensure_ascii=False,indent=2)
arr='\n'.join('  '+l if i else l for i,l in enumerate(arr.split('\n')))
out=src[:m.start(2)]+arr+src[m.end(2):]
if '\r\n' in src: out=out.replace('\r\n','\n').replace('\n','\r\n')
io.open(P,'w',encoding='utf-8',newline='').write(out)
print('applied')
