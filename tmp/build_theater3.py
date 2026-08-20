import json,re,io,sys,datetime
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
data=json.load(open('tmp/parsed50.json',encoding='utf-8'))
dd=json.load(open('tmp/theater_dedup.json',encoding='utf-8'))[100:150]
ddmap={o['artist']:o['urls'] for o in dd}
WD='月火水木金土日'
def wd(iso):
    y,m,d=map(int,iso.split('-')); return WD[datetime.date(y,m,d).weekday()]
def prefshort(p): return p if p=='北海道' else re.sub(r'(都|道|府|県)$','',p)
def md(iso): y,m,d=iso.split('-'); return f"{int(m)}/{int(d)}"
def jp(iso): y,m,d=map(int,iso.split('-')); return f"{y}年{m}月{d}日({wd(iso)})"
def ecd_url(turl):
    mm=re.search(r'eventCd=(\w+)',turl or '')
    return 'https://t.pia.jp/pia/event/event.do?eventCd='+mm.group(1) if mm else None
def kenshu(title):
    if '／' in title:
        return (re.sub(r'＜.*?＞','',title.split('／')[0]).strip('　 ').strip()) or '一般発売'
    m=re.search(r'(プレイガイド最速先行|最速先行|オフィシャル先行|\d次プレリザーブ|プレリザーブ\d次|プレリザーブ|\d次受付|プリセール|一般発売|当日引換券|当日券|先行)',title)
    return m.group(1) if m else '先行'
def parse_when(state,when):
    if state=='発売前':
        m=re.search(r'(\d{4})/(\d{1,2})/(\d{1,2})\([^)]*\)\s*(?:昼|夜|朝|午前|午後)?(\d{1,2}:\d{2})?\s*より発売',when)
        if m:
            iso=f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"; t=m.group(4)
            return (f"{int(m.group(2))}/{int(m.group(3))} {t}発売" if t else f"{int(m.group(2))}/{int(m.group(3))}発売"),iso,iso
    else:
        m=re.search(r'～\s*(\d{4})/(\d{1,2})/(\d{1,2})\([^)]*\)\s*(?:昼|夜|朝|午前|午後)?(\d{1,2}:\d{2})?',when)
        if m:
            iso=f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"; t=m.group(4)
            return (f"〜{int(m.group(2))}/{int(m.group(3))} {t}" if t else f"〜{int(m.group(2))}/{int(m.group(3))}"),iso,None
    return None,None,None
def genre_of(n):
    if re.search(r'落語|寄席|独演会|二人会|お笑い|漫才|ものまね|コント|新喜劇|喜劇|講談|演芸',n): return 'owarai'
    if re.search(r'狂言|能楽|文楽|歌舞伎|雅楽|邦楽',n): return 'dento'
    if re.search(r'バレエ|オペラ|クラシック|交響|管弦|フィル',n): return 'classic'
    return 'engeki'

entries=[];skipped=[]
for o in data:
    if o['nbuy']==0: skipped.append(o['newid']);continue
    rows=o['buyable']
    venues=list(dict.fromkeys(r['venue'] for r in rows if r['venue']))
    prefs=list(dict.fromkeys(prefshort(r['pref']) for r in rows if r['pref']))
    perfs=sorted(set(r['perfdate'] for r in rows if r['perfdate'])); perfends=sorted(set((r.get('perf_end') or r['perfdate']) for r in rows if r['perfdate']))
    ecds=set(re.search(r'eventCd=(\w+)',r['url']).group(1) for r in rows if r.get('url') and re.search(r'eventCd=(\w+)',r['url']))
    multi=len(ecds)>1
    tickets=[]
    for r in rows:
        suf,iso,sd=parse_when(r['state'],r['when'])
        if not iso: continue
        pe=r.get('perf_end') or r['perfdate']
        mdr=md(r['perfdate']) if pe==r['perfdate'] else f"{md(r['perfdate'])}〜{md(pe)}"
        typ=f"{kenshu(r['title'])}（{prefshort(r['pref'])} {mdr}公演）{suf}"
        t={'type':typ,'date':iso}
        if sd: t['startDate']=sd
        if multi and ecd_url(r['url']): t['url']=ecd_url(r['url'])
        tickets.append(t)
    tickets.sort(key=lambda t:t['date'])
    evdate=perfends[-1] if perfends else ''
    venue=venues[0] if len(venues)==1 else '全国ツアー（'+'／'.join(venues[:4])+'）'
    pref=prefs[0] if len(prefs)==1 else '全国'
    if len(perfs)==1 and perfends[-1]==perfs[0]: dl=f"{jp(perfs[0])} {pref} {venues[0] if venues else ''}".strip()
    else: dl=f"{jp(perfs[0])}〜{jp(perfends[-1])} {'全国ツアー' if pref=='全国' else (pref+' '+(venues[0] if len(venues)==1 else ''))}".strip()
    u0=ddmap.get(o['artist'],[''])[0]
    if 'eventBundleCd' in u0:
        pia='https://t.pia.jp/pia/event/event.do?eventBundleCd='+re.search(r'eventBundleCd=(\w+)',u0).group(1)
    else:
        pia=ecd_url(u0)
    entries.append({'id':o['newid'],'artist':o['artist'],'name':o['artist'],'date':evdate,
       'dateLabel':dl,'venue':venue,'prefecture':pref,'genre':'new','_genre':genre_of(o['artist']),
       'price':None,'links':{'rakuten':None,'lawson':None,'pia':pia,'eplus':None},
       'tickets':tickets,'verified':True,'verifiedAt':'2026-06-19'})
json.dump(entries,open('tmp/theater3_entries.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('構築',len(entries),'件 / skip',skipped)
for e in entries[:7]:
    print(e['id'],e['prefecture'],'|',e['dateLabel'][:38])
    for t in e['tickets']: print('     ',t['type'])
