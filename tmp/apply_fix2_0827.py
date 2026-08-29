# -*- coding: utf-8 -*-
"""道具修正後の再ビルドを【追加と補完だけ】で当てる（置換しない）。
   🚨1回目は置換にして id=72 劇団四季の「ぴあシート」6枠（全部これからの公演）を落とした。
     枠は絶対に消さない。やることは3つだけ:
       ① links.pia を「実際に買える枠があるページ」に直す
       ② 既存の枠で url が空のものに、再ビルド側の同じ券種名の url を入れる
       ③ 再ビルドにしか無い枠を足す
   🚨index.html は CRLF。newline='' で読み書きする。"""
import io,re,json,sys,shutil
sys.stdout.reconfigure(encoding='utf-8')
reb={e['id']:e for e in json.load(io.open('tmp/rebuilt_fix_0827.json',encoding='utf-8'))}
P='index.html'; shutil.copy(P,'index.html.bak_0827_fixmulti2')
src=io.open(P,encoding='utf-8',newline='').read()
m=re.search(r'(  const EVENTS = )(\[.*?\])(;)',src,re.S)
EVENTS=json.loads(m.group(2))
log=io.open('tmp/fix_applied_0827.md','w',encoding='utf-8')
log.write('# 2026-08-27 build_pia_entries のバグ修正ぶんを当てる（追加と補完のみ・枠は1つも消さない）\n\n')
nlink=nurl=nadd=0
for e in EVENTS:
    b=reb.get(e['id'])
    if not b: continue
    old=e.get('tickets') or []
    bytype={t.get('type'):t for t in (b.get('tickets') or [])}
    lines=[]
    # ① links.pia
    oldpia=(e.get('links') or {}).get('pia')
    newpia=b.get('links',{}).get('pia')
    if newpia and newpia!=oldpia:
        e.setdefault('links',{})['pia']=newpia; nlink+=1
        lines.append('  🔧 links.pia %s → %s'%(oldpia,newpia))
    # ② urlの補完
    for t in old:
        if not t.get('url'):
            src_t=bytype.get(t.get('type'))
            if src_t and src_t.get('url'):
                t['url']=src_t['url']; nurl+=1
                lines.append('  🔗 url補完 %s → %s'%(t.get('type'),t['url']))
    # ③ 追加
    have={t.get('type') for t in old}
    add=[t for t in (b.get('tickets') or []) if t.get('type') not in have]
    if add:
        e['tickets']=old+add; nadd+=len(add)
        for t in add: lines.append('  + %s | %s | %s'%(t.get('type'),t.get('date'),t.get('url')))
    if lines:
        log.write('## id=%d %s 枠 %d→%d\n'%(e['id'],e.get('artist'),len(old),len(e['tickets'])))
        log.write('\n'.join(lines)+'\n\n')
arr=json.dumps(EVENTS,ensure_ascii=False,indent=2)
arr='\n'.join('  '+l if i else l for i,l in enumerate(arr.split('\n')))
out=src[:m.start(2)]+arr+src[m.end(2):]
if '\r\n' in src: out=out.replace('\r\n','\n').replace('\n','\r\n')
io.open(P,'w',encoding='utf-8',newline='').write(out)
log.close()
print('links.pia 修正 %d件 / url補完 %d枠 / 枠追加 %d枠（削除 0枠）'%(nlink,nurl,nadd))
