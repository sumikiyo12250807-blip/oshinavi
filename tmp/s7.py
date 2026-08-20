import re,html
t=open('tmp/pia_artist.html',encoding='utf-8',errors='replace').read()
t=re.sub(r'<script.*?</script>','',t,flags=re.S); t=re.sub(r'<style.*?</style>','',t,flags=re.S)
t=re.sub(r'<[^>]+>','\n',t); t=html.unescape(t)
L=[l.strip() for l in t.split('\n') if l.strip()]
s='\n'.join(L)
i=s.find('榛葉樹人')
open('tmp/pia_artist.txt','w',encoding='utf-8').write(s)
