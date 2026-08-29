# -*- coding: utf-8 -*-
"""rlsIn の各値が何を返しているかを、行の『発売種別／状態／期間』で実測する。"""
import re,sys,time,urllib.request,html
sys.stdout.reconfigure(encoding='utf-8')
def text(h):
    t=re.sub(r'<script.*?</script>','',h,flags=re.S); t=re.sub(r'<style.*?</style>','',t,flags=re.S)
    t=re.sub(r'<[^>]+>','\n',t); t=html.unescape(t)
    return [l.strip() for l in t.split('\n') if l.strip()]
STATES=('販売期間中','抽選受付中','販売前','受付前','発売前','販売開始','先着受付中','受付中')
for rls in ['01','02','03','04','05','06']:
    url='https://t.pia.jp/pia/rlsInfo.do?lg=01&rlsIn=%s&page=1'%rls
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
    h=urllib.request.urlopen(req,timeout=30).read().decode('utf-8','replace')
    L=text(h)
    tot=re.search(r'全([\d,]+)件中',' '.join(L))
    rows=[l for l in L if any(l.startswith(s) for s in STATES) or re.match(r'^\d{4}/\d{1,2}/\d{1,2}.*(発売|受付)',l)]
    print('=== rlsIn=%s  総件数=%s'%(rls, tot.group(1) if tot else '?'))
    for l in rows[:6]: print('    ',l)
    time.sleep(3)
