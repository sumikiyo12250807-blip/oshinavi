# -*- coding: utf-8 -*-
"""ツアー分裂の回収＝既存エントリに「未登録だった公演の枠」を足す（2026-08-21版の踏襲）。

🚨【置換ではなく追加】既存の枠には会場名つきバッジなど手を入れた情報が入っていることがあり、
   置換すると失う（2026-08-21 天皇杯で実例）。soldout枠・e+/楽天の枠も守られる。
🚨公演日(date)は**後ろへ伸びる時だけ**更新する（縮む方向は「1公演ぶんしか見ていない」サイン）。
🚨index.html は CRLF。newline='' で読み書きする。
"""
import io,re,json,sys,shutil
sys.stdout.reconfigure(encoding='utf-8')
def key(t):
    u=re.sub(r'^https?://[^/]+','',t.get('url') or '').replace('/pia/event/event.do','/pia/event.do')
    return (t.get('type'),u)
reb={e['id']:e for e in json.load(io.open('tmp/built_article_exist_0830.json',encoding='utf-8'))}
P='index.html'
shutil.copy(P,'index.html.bak_0830_article')
src=io.open(P,encoding='utf-8',newline='').read()
m=re.search(r'(  const EVENTS = )(\[.*?\])(;)',src,re.S)
EVENTS=json.loads(m.group(2))
log=io.open('tmp/merge_applied_article_0830.md','w',encoding='utf-8')
log.write('# 2026-08-29 記事の再照合で見つかった取りこぼしの回収の統合（追加のみ・置換なし）\n\n')
nent=nslot=ndate=0
for e in EVENTS:
    b=reb.get(e['id'])
    if not b: continue
    old=e.get('tickets') or []
    seen={key(t) for t in old}
    add=[t for t in (b.get('tickets') or []) if key(t) not in seen]
    grew = b.get('date') and b['date']>(e.get('date') or '')
    if not add and not grew: continue
    nent+=1
    log.write('## id=%d %s 枠 %d→%d\n'%(e['id'],e.get('artist'),len(old),len(old)+len(add)))
    for t in add:
        log.write('  + %s | 締切/発売 %s | %s\n'%(t.get('type'),t.get('date'),t.get('url') or '(entry links)'))
    if grew:
        log.write('  公演日 %s → %s（千秋楽が後ろに伸びた）\n'%(e.get('date'),b['date']))
        e['date']=b['date']
        for k in ('dateLabel','venue','prefecture'):
            if b.get(k): e[k]=b[k]
        ndate+=1
    log.write('\n')
    e['tickets']=old+add
    nslot+=len(add)
arr=json.dumps(EVENTS,ensure_ascii=False,indent=2)
arr='\n'.join('  '+l if i else l for i,l in enumerate(arr.split('\n')))
out=src[:m.start(2)]+arr+src[m.end(2):]
if '\r\n' in src: out=out.replace('\r\n','\n').replace('\n','\r\n')
io.open(P,'w',encoding='utf-8',newline='').write(out)
log.write('\n合計 %d エントリ / +%d 枠 / 公演日が伸びた %d件\n'%(nent,nslot,ndate))
log.close()
print('統合 %d エントリ / 追加 %d 枠 / 千秋楽が伸びた %d件 → tmp/merge_applied_article_0830.md'%(nent,nslot,ndate))
