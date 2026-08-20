import re,html
raw=open('tmp/mh_vol4.html','rb').read()
for enc in ['utf-8','cp932','euc-jp']:
    try: t=raw.decode(enc); break
    except: continue
t=re.sub(r'<script.*?</script>','',t,flags=re.S)
t=re.sub(r'<style.*?</style>','',t,flags=re.S)
t=re.sub(r'<br\s*/?>','\n',t)
t=re.sub(r'<a ([^>]*)>',lambda m:'\n[LINK '+ (re.search(r'href="([^"]+)"',m.group(1)).group(1) if re.search(r'href="([^"]+)"',m.group(1)) else '')+'] ',t)
t=re.sub(r'<[^>]+>','\n',t)
t=html.unescape(t)
lines=[l.strip() for l in t.split('\n') if l.strip()]
open('tmp/mh_vol4.txt','w',encoding='utf-8').write('ENC=%s\n'%enc+'\n'.join(lines))
