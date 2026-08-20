import re,html
raw=open('tmp/pia_pcode.html','rb').read()
t=raw.decode('utf-8','replace')
t=re.sub(r'<script.*?</script>','',t,flags=re.S); t=re.sub(r'<style.*?</style>','',t,flags=re.S)
t=re.sub(r'<[^>]+>','\n',t); t=html.unescape(t)
L=[l.strip() for l in t.split('\n') if l.strip()]
open('tmp/pia_pcode.txt','w',encoding='utf-8').write('\n'.join(L[:120]))
