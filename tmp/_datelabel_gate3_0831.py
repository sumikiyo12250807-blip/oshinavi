# dateLabel と tickets の「公演日」が食い違うエントリを検出する（第3版）
#  修正点: 公演日は「（… M/D公演）」のカッコの中だけから拾う。カッコ外の M/D は発売日なので拾わない
import json,re,sys,datetime
sys.stdout.reconfigure(encoding='utf-8')
s=open('index.html',encoding='utf-8').read()
ev=json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);\s*\n',s,re.S).group(1))
def d(y,m,da):
    try: return datetime.date(y,m,da)
    except ValueError: return None
PAREN=re.compile(r'[（(]([^（()）]*?公演)[)）]')
def show_dates(e):
    out=set()
    for t in e.get('tickets',[]):
        ty=t.get('type','')
        anchor=t.get('date') or e['date']
        ay=int(anchor[:4]); ad=d(*map(int,anchor.split('-')))
        for pm in PAREN.finditer(ty):
            seg=pm.group(1)
            for m in re.finditer(r'(R9年\s*)?(\d{1,2})/(\d{1,2})',seg):
                mo,da=int(m.group(2)),int(m.group(3))
                if m.group(1): c=d(2027,mo,da)
                else:
                    cands=[x for x in (d(ay-1,mo,da),d(ay,mo,da),d(ay+1,mo,da)) if x]
                    if not cands or not ad: continue
                    c=min(cands,key=lambda x:abs((x-ad).days))
                if c: out.add(c)
    return sorted(out)
def label_range(lab):
    ds=[];y=None
    for m in re.finditer(r'(?:(\d{4})年)?(\d{1,2})月(\d{1,2})日',lab or ''):
        if m.group(1): y=int(m.group(1))
        if y is None: continue
        x=d(y,int(m.group(2)),int(m.group(3)))
        if x: ds.append(x)
    return ds
bad=[]
for e in ev:
    sd=show_dates(e); lr=label_range(e.get('dateLabel',''))
    if not sd or not lr: continue
    lo,hi=min(lr),max(lr); smin,smax=sd[0],sd[-1]
    over=max((smax-hi).days,0); under=max((lo-smin).days,0)
    if over>1 or under>1:
        bad.append((e['id'],e.get('artist','')[:30],e['date'],e.get('dateLabel','')[:46],f"{smin}〜{smax}",over,under))
print('dateLabel が実際の公演日をカバーしていない:',len(bad),'件 / 全',len(ev))
bad.sort(key=lambda x:-(x[5]+x[6]))
for b in bad[:40]:
    print(f"  id={b[0]:5} {b[1]:32} date={b[2]} label[{b[3]}] 実公演={b[4]} 後{b[5]}日 前{b[6]}日")
json.dump([b[0] for b in bad],open('tmp/_datelabel_bad_0831.json','w'))
