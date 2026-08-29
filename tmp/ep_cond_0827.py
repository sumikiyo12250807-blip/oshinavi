# -*- coding: utf-8 -*-
"""e+の公演ページから 開演時刻 と 先行の条件（FC限定かどうか）の記述を機械で抜く。"""
import re,sys,io,urllib.request,html as H,json
sys.stdout.reconfigure(encoding='utf-8')
URLS=sys.argv[1:]
o=io.open('tmp/ep_cond_0827.md','w',encoding='utf-8')
for u in URLS:
    req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})
    h=urllib.request.urlopen(req,timeout=30).read().decode('utf-8','replace')
    o.write('## %s\n'%u)
    # JSON-LD
    for m in re.finditer(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>',h,re.S):
        try:
            d=json.loads(H.unescape(m.group(1).strip()))
        except Exception: continue
        for x in (d if isinstance(d,list) else [d]):
            if isinstance(x,dict) and x.get('@type') in ('Event','MusicEvent','TheaterEvent'):
                loc=x.get('location') or {}
                o.write('- LD: name=%s start=%s venue=%s\n'%(x.get('name'),x.get('startDate'),
                        (loc.get('name') if isinstance(loc,dict) else loc)))
    t=re.sub(r'<script.*?</script>','',h,flags=re.S)
    t=re.sub(r'<style.*?</style>','',t,flags=re.S)
    t=re.sub(r'<[^>]+>','\n',t); t=H.unescape(t)
    L=[l.strip() for l in t.split('\n') if l.strip()]
    # 条件らしい語を含む行
    KW=['会員','ファンクラブ','ＦＣ','FC','限定','対象','資格','入会','登録','抽選','先行','おひとり','枚数制限','開演','開場']
    hit=[l for l in L if any(k in l for k in KW)]
    for l in hit[:35]: o.write('   | %s\n'%l[:160])
    o.write('\n')
o.close()
print('wrote tmp/ep_cond_0827.md')
