# 統合入力を作る：既存URLも必ず一緒に渡す（feedback_build_pia_multiurl_loses_ticket_url）
import json,re,sys,unicodedata
sys.stdout.reconfigure(encoding='utf-8')
d=json.load(open('tmp/_cand_0831.json',encoding='utf-8'))
s=open('index.html',encoding='utf-8').read()
ev=json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);\s*\n',s,re.S).group(1))
def norm(x):
    x=unicodedata.normalize('NFKC',x or '')
    return re.sub(r'[\s　・･/／「」『』【】（）()\[\]~〜\-–—!！?？,、。.＆&]','',x).lower()
byname={}
for e in ev:
    byname.setdefault(norm(e.get('artist','')),[]).append(e)
# 手で決めた統合先（劇団四季まわり・N響）
MANUAL={'劇団四季「オペラ座の怪人」／名古屋':4625,
 '劇団四季ミュージカル『コーラスライン』／岐阜':4898,
 '劇団四季ミュージカル『コーラスライン』／名古屋':4898,
 '劇団四季ミュージカル『コーラスライン』／稲沢':4898,
 '劇団四季ミュージカル『コーラスライン』／四日市':4898,
 'N響「第9」':4843}
byid={e['id']:e for e in ev}
groups={}
def add(tid,url):
    groups.setdefault(tid,set()).add(url)
for it in d['exact']:
    hits=byname.get(norm(it['artist']),[])
    if len(hits)!=1:
        print('⚠️統合先が一意でない:',it['artist'][:40],[h['id'] for h in hits]); continue
    add(hits[0]['id'],it['url'])
for it in d['fresh']:
    if it['artist'] in MANUAL: add(MANUAL[it['artist']],it['url'])
# エージェントが見つけた取りこぼし（買える枠を実ページで確認済みの4件）
EXTRA={'ビッケブランカ':'https://t.pia.jp/pia/event/event.do?eventCd=2625982',
 'Guiano':'https://t.pia.jp/pia/event/event.do?eventCd=2624545',
 'MYTH & ROID':'https://t.pia.jp/pia/event/event.do?eventCd=2622453',
 '夕闇に誘いし漆黒の天使達':'https://t.pia.jp/pia/event/event.do?eventCd=2628428'}
for nm,u in EXTRA.items():
    hits=byname.get(norm(nm),[])
    if len(hits)!=1:
        print('⚠️取りこぼしの統合先が一意でない:',nm,[h['id'] for h in hits]); continue
    add(hits[0]['id'],u)
out=[]
for tid,urls in sorted(groups.items()):
    e=byid[tid]
    ex=[]
    L=e.get('links') or {}
    if L.get('pia'): ex.append(L['pia'])
    for t in e.get('tickets',[]):
        if t.get('url') and t['url'] not in ex: ex.append(t['url'])
    out.append({'newid':tid,'artist':e.get('artist',''),'urls':ex+[u for u in sorted(urls) if u not in ex]})
json.dump(out,open('tmp/_merge_in_0831.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('統合対象',len(out),'エントリ / 渡すURL計',sum(len(o['urls']) for o in out))
