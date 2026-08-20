import json,re,urllib.request,html as _html,io,sys,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
dd=json.load(open('tmp/theater_dedup.json',encoding='utf-8'))[100:150]
parsed={o['newid']:o for o in json.load(open('tmp/parsed50.json',encoding='utf-8'))}
def fetch(u):
    req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})
    return urllib.request.urlopen(req,timeout=30).read().decode('utf-8','replace')
# map newid->urls via artist order (parsed50 built from dd[100:150] in order, nid=maxid+1+idx)
out={}
nid_base=parsed[min(parsed)]['newid']
for idx,o in enumerate(dd):
    nid=nid_base+idx
    urls=o['urls']
    ranges=set()
    try:
        for u in urls:
            h=fetch(u); time.sleep(0.2)
            # per item: collect datetime pairs
            for it in re.split(r'(?=<li class="ticketSalesList-2024__item)',h):
                if 'ticketSalesCard-2024__status' not in it: continue
                dts=re.findall(r'datetime="(\d{4}-\d{2}-\d{2})',it)
                if len(dts)>=2 and dts[0]!=dts[-1]:
                    ranges.add((dts[0],dts[-1]))
                elif dts:
                    ranges.add((dts[0],dts[0]))
    except Exception as ex:
        out[nid]=('ERR',str(ex)); continue
    multi=[r for r in ranges if r[0]!=r[1]]
    if multi:
        out[nid]=multi
for nid in sorted(out):
    print(nid, parsed[nid]['artist'][:28] if nid in parsed else '?', '→', out[nid])
print('複数日公演の数:',len(out))
