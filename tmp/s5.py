import re,html
for n in ['mh_form','mh_ci']:
    raw=open('tmp/%s.html'%n,'rb').read()
    for enc in ['utf-8','cp932','euc-jp']:
        try: t=raw.decode(enc); break
        except: continue
    t=re.sub(r'<script.*?</script>','',t,flags=re.S); t=re.sub(r'<style.*?</style>','',t,flags=re.S)
    t=re.sub(r'<br\s*/?>','\n',t); t=re.sub(r'<[^>]+>','\n',t); t=html.unescape(t)
    L=[l.strip() for l in t.split('\n') if l.strip()]
    open('tmp/%s.txt'%n,'w',encoding='utf-8').write('\n'.join(L))
