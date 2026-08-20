import re,html
h=open('tmp/eplus_kw1.html',encoding='utf-8',errors='replace').read()
t=re.sub(r'<script.*?</script>','',h,flags=re.S)
t=re.sub(r'<style.*?</style>','',t,flags=re.S)
t=re.sub(r'<[^>]+>','\n',t)
t=html.unescape(t)
lines=[l.strip() for l in t.split('\n')]
lines=[l for l in lines if l]
open('tmp/z_out.txt','w',encoding='utf-8').write('\n'.join(lines))
