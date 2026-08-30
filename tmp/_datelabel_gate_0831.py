# dateLabel（画面に出る公演期間）と tickets の公演日が食い違うエントリを機械で検出する
import json,re,sys,datetime
sys.stdout.reconfigure(encoding='utf-8')
s=open('index.html',encoding='utf-8').read()
ev=json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);\s*\n',s,re.S).group(1))

def show_dates(e):
    """ticket.type の「（県 M/D公演）」「（県 M/D〜M/D公演）」「R9年 M/D」から公演日を全部拾う"""
    out=set()
    base=int(e['date'][:4])
    for t in e.get('tickets',[]):
        ty=t.get('type','')
        for m in re.finditer(r'(R9年\s*)?(\d{1,2})/(\d{1,2})\s*(?:〜|~|公演)',ty):
            y=2027 if m.group(1) else None
            mo,da=int(m.group(2)),int(m.group(3))
            if y is None:
                # 年跨ぎ: 公演日が entry.date より大きく前なら翌年扱い
                y=base
                try: d=datetime.date(y,mo,da)
                except ValueError: continue
                ed=datetime.date(*map(int,e['date'].split('-')))
                if (d-ed).days>200: y=base-1
                elif (ed-d).days>200: y=base+1
            try: out.add(datetime.date(y,mo,da))
            except ValueError: pass
    return sorted(out)

def label_range(lab):
    ds=[]
    for m in re.finditer(r'(\d{4})年(\d{1,2})月(\d{1,2})日',lab or ''):
        try: ds.append(datetime.date(int(m.group(1)),int(m.group(2)),int(m.group(3))))
        except ValueError: pass
    return ds

bad=[]
for e in ev:
    sd=show_dates(e)
    if not sd: continue
    lr=label_range(e.get('dateLabel',''))
    if not lr: continue
    lo,hi=min(lr),max(lr)
    smin,smax=sd[0],sd[-1]
    # 判定: ticket の公演日がラベルの範囲からはみ出しているか
    if smax>hi or smin<lo:
        bad.append((e['id'],e.get('artist','')[:34],e['date'],e.get('dateLabel','')[:44],
                    f"{smin}〜{smax}", (smax-hi).days if smax>hi else 0))
print('dateLabel と公演日が食い違うエントリ:',len(bad),'件 / 全',len(ev))
bad.sort(key=lambda x:-x[5])
for b in bad[:60]:
    print(f"  id={b[0]:5} {b[1]:36} date={b[2]} label[{b[3]}] 実公演日={b[4]} はみ出し{b[5]}日")
json.dump([b[0] for b in bad],open('tmp/_datelabel_bad_0831.json','w'))
