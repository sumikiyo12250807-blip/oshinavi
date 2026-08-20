import re,html,sys
for name in ['mh_vol3','mh_top']:
    raw=open('tmp/%s.html'%name,'rb').read()
    for enc in ['utf-8','cp932','euc-jp']:
        try:
            t=raw.decode(enc); break
        except: continue
    t=re.sub(r'<script.*?</script>','',t,flags=re.S)
    t=re.sub(r'<style.*?</style>','',t,flags=re.S)
    t=re.sub(r'<br\s*/?>','\n',t)
    t=re.sub(r'<[^>]+>','\n',t)
    t=html.unescape(t)
    lines=[l.strip() for l in t.split('\n')]
    lines=[l for l in lines if l]
    open('tmp/%s.txt'%name,'w',encoding='utf-8').write('ENC=%s\n'%enc+'\n'.join(lines))
