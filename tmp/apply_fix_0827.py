# -*- coding: utf-8 -*-
"""道具のバグ修正後に再ビルドした15件を当てる。
   🚨ぴあ由来の枠は再ビルド結果で置き換える（url と links.pia を正しくするため）が、
     **売り切れ枠（予定枚数終了）とぴあ以外の売り場の枠は必ず残す**
     （feedback_soldout_keep_visible / feedback_delete_nonpia_blindspot）。
   🚨index.html は CRLF。newline='' で読み書きする。"""
import io,re,json,sys,shutil
sys.stdout.reconfigure(encoding='utf-8')
reb={e['id']:e for e in json.load(io.open('tmp/rebuilt_fix_0827.json',encoding='utf-8'))}
P='index.html'; shutil.copy(P,'index.html.bak_0827_fixmulti')
src=io.open(P,encoding='utf-8',newline='').read()
m=re.search(r'(  const EVENTS = )(\[.*?\])(;)',src,re.S)
EVENTS=json.loads(m.group(2))
log=io.open('tmp/fix_applied_0827.md','w',encoding='utf-8')
log.write('# 2026-08-27 build_pia_entries のバグ修正後の当て直し（15件）\n\n')
n=0
for e in EVENTS:
    b=reb.get(e['id'])
    if not b: continue
    old=e.get('tickets') or []
    keep=[t for t in old if t.get('soldout') or (t.get('url') and 't.pia.jp' not in t['url'])]
    newt=b.get('tickets') or []
    types={t.get('type') for t in newt}
    keep=[t for t in keep if t.get('type') not in types]
    e['tickets']=newt+keep
    oldpia=(e.get('links') or {}).get('pia')
    if b['links'].get('pia'): e.setdefault('links',{})['pia']=b['links']['pia']
    log.write('## id=%d %s 枠 %d→%d（残した売切/他社枠 %d）\n'%(e['id'],e.get('artist'),len(old),len(e['tickets']),len(keep)))
    if oldpia!=e['links']['pia']:
        log.write('  🔧 links.pia %s → %s\n'%(oldpia,e['links']['pia']))
    for t in e['tickets']:
        log.write('   * %s | %s | %s\n'%(t.get('type'),t.get('date'),t.get('url') or '(なし)'))
    log.write('\n'); n+=1
arr=json.dumps(EVENTS,ensure_ascii=False,indent=2)
arr='\n'.join('  '+l if i else l for i,l in enumerate(arr.split('\n')))
out=src[:m.start(2)]+arr+src[m.end(2):]
if '\r\n' in src: out=out.replace('\r\n','\n').replace('\n','\r\n')
io.open(P,'w',encoding='utf-8',newline='').write(out)
log.close()
print('当て直し %d件 → tmp/fix_applied_0827.md'%n)
