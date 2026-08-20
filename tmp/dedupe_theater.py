import json,io,sys,unicodedata,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
d=json.load(open('tmp/presale_02.json',encoding='utf-8'))['new']
def norm(s): return unicodedata.normalize('NFKC',s or '').strip()
groups={}
for x in d:
    key=norm(x['artist'])
    g=groups.setdefault(key,{'artist':x['artist'],'urls':set(),'perfs':set(),'prefs':set(),'rls':set(),'saletype':set()})
    g['urls'].add(x['url']); g['perfs'].add(x['perfdate']); g['prefs'].add(x['pref'])
    if x.get('rlsdate'):g['rls'].add(x['rlsdate'])
    g['saletype'].add(x['saletype'])
print('ユニーク公演(名寄せ後):',len(groups))
# save deduped
out=[]
for k,g in groups.items():
    out.append({'artist':g['artist'],'urls':sorted(g['urls']),'perfs':sorted(g['perfs']),'prefs':sorted(g['prefs']),'rls':sorted(g['rls']),'saletype':sorted(g['saletype'])})
# sort by earliest rls date then name
def rkey(o): 
    return (min(o['rls']) if o['rls'] else '9999', o['artist'])
out.sort(key=rkey)
json.dump(out,open('tmp/theater_dedup.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('保存 tmp/theater_dedup.json')
print('\n=== 先頭60件(名寄せ後) ===')
for i,o in enumerate(out[:60]):
    multi='[ツアー%d公演]'%len(o['urls']) if len(o['urls'])>1 else ''
    print(f"{i+1:3} | {(min(o['rls']) if o['rls'] else '?'):9} | {o['artist'][:34]} {multi} | {'/'.join(o['prefs'][:3])}")
