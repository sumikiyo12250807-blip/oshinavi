# -*- coding: utf-8 -*-
import re,io,sys,json,unicodedata
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
ev={str(e['id']):e for e in json.load(open('tmp/_agentP1_events.json',encoding='utf-8'))}
pia=json.load(open('tmp/_agentP1_parsed.json',encoding='utf-8'))
GEN={'5747':'音楽 フェスティバル','5766':'音楽 J-POP・ROCK','5784':'音楽 J-POP・ROCK',
     '5794':'音楽 J-POP・ROCK','5824':'音楽 海外ROCK・POPS'}
TITLEGEN={}  # <title>から拾った分
import os
for eid,v in pia.items():
    g=v['genre']
    if not g:
        h=open('tmp/_agentP1_html/%s.html'%eid,encoding='utf-8').read()
        t=re.search(r'<title>.*?\[(.*?)のチケット',h,re.S)
        g=t.group(1) if t else GEN.get(eid,'')
    if not g: g=GEN.get(eid,'')
    v['genre2']=g
def norm(s):
    s=unicodedata.normalize('NFKC',s or '')
    return re.sub(r'[\s　]+','',s).replace('／','/').replace('~','～').lower()
issues=[]
for eid,v in pia.items():
    p=v['line'].split('|')
    e=ev.get(eid)
    buy=[c for c in v['cards'] if c['state'] in ('受付中','発売前')]
    # 1 枠数
    n_reg=len(e['tickets']) if e else int(p[4])
    if n_reg!=len(buy):
        issues.append((eid,'買える枠数',str(n_reg),str(len(buy))))
    if int(p[4])!=n_reg:
        issues.append((eid,'枠数(ファイル vs index.html)',p[4],str(n_reg)))
    # 2 千秋楽
    alld=[c['pe'] for c in v['cards'] if c['pe']]
    buyd=[c['pe'] for c in buy if c['pe']]
    reg_date=e['date'] if e else p[2]
    if reg_date!=max(buyd or ['']):
        issues.append((eid,'千秋楽(買える枠の最大公演日)',reg_date,max(buyd) if buyd else '-'))
    if max(alld or [''])!=max(buyd or ['']):
        issues.append((eid,'※ページ全体の最大公演日(終了枠含む)',max(buyd) if buyd else '-',max(alld)))
    # 3 県
    prefs=[]
    for c in buy:
        src=c['pref'] or c['venue']
        for x in re.split(r'[／/]',src):
            x=x.strip()
            if re.search(r'(都|道|府|県)$',x): prefs.append(x)
    prefs=list(dict.fromkeys(prefs))
    short=[re.sub(r'(都|府|県)$','',x) for x in prefs]
    reg_pref=(e['prefecture'] if e else p[3])
    if norm('・'.join(short))!=norm(reg_pref):
        issues.append((eid,'県',reg_pref,'・'.join(short) if short else '-'))
    # 4 名前
    reg_name=(e['artist'] if e else p[1])
    if norm(reg_name) not in norm(v['name']) and norm(v['name']) not in norm(reg_name):
        issues.append((eid,'公演名/アーティスト名',reg_name,v['name']))
    # 5 ジャンル
    regsub=(e.get('_piaSub') or '') if e else ''
    if norm(regsub.replace('/','')) != norm(v['genre2'].replace(' ','')):
        issues.append((eid,'ぴあジャンル(_piaSub)',regsub or '(なし)',v['genre2'] or '(取得できず)'))
    # 6 発売前/受付中の取り違え（ticketのstartDate有無 vs ぴあの状態）
    n_before=sum(1 for c in buy if c['state']=='発売前')
    n_active=len(buy)-n_before
    t_before=sum(1 for t in (e['tickets'] if e else []) if t.get('startDate'))
    t_active=len(e['tickets'])-t_before if e else 0
    if e and (n_before,n_active)!=(t_before,t_active):
        issues.append((eid,'発売前/受付中の内訳',f'発売前{t_before}/受付中{t_active}',f'発売前{n_before}/受付中{n_active}'))
print('検査対象', len(pia),'件 / index.htmlに存在', sum(1 for k in pia if k in ev))
print('ズレ件数(項目単位)',len(issues))
print()
for it in sorted(issues,key=lambda x:(x[0],x[1])):
    print(' | '.join(it))
