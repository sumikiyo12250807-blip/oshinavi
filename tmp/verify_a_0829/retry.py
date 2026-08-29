import os,re,subprocess,time,glob
RAW='C:/Users/user/oshinavi/tmp/verify_a_0829/raw'
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
def url_of(name):
    n=name[:-5]
    if n.startswith('event_event_do_'):
        r=n[len('event_event_do_'):]
        if r.startswith('eventBundleCd_'):
            return 'https://t.pia.jp/pia/event/event.do?eventBundleCd='+r.split('_',1)[1]
        return 'https://t.pia.jp/pia/event/event.do?eventCd='+r.split('_',1)[1]
    if n.startswith('ticketInformation_do_'):
        r=n[len('ticketInformation_do_'):]
        if r.startswith('lotRlsCd_'):
            return 'https://t.pia.jp/pia/ticketInformation.do?lotRlsCd='+r.split('_',1)[1]
        m=re.match(r'eventCd_(\d+)_rlsCd_(\w+)$',r)
        if m: return 'https://t.pia.jp/pia/ticketInformation.do?eventCd=%s&rlsCd=%s'%(m.group(1),m.group(2))
    return None
bad=[f for f in os.listdir(RAW) if os.path.getsize(os.path.join(RAW,f))<2000]
print('bad',len(bad))
for f in bad:
    u=url_of(f)
    if not u:
        print('SKIP-unknown',f); continue
    ok=False
    for attempt in range(4):
        p=os.path.join(RAW,f)
        subprocess.run(['curl','-s','--max-time','60','-A',UA,u,'-o',p])
        if os.path.getsize(p)>2000:
            h=open(p,encoding='utf-8',errors='replace').read()
            if 'アクセスが集中' in h or 'ただいま大変混み合' in h:
                time.sleep(30); continue
            ok=True; break
        time.sleep(15)
    print(('OK ' if ok else 'FAIL '),f,u,flush=True)
    time.sleep(2)
print('RETRYDONE')
