# -*- coding: utf-8 -*-
import re,sys,html
sys.stdout.reconfigure(encoding='utf-8')
h=open('tmp/rlsinfo_lg01.html',encoding='utf-8').read()
t=re.sub(r'<script.*?</script>','',h,flags=re.S)
t=re.sub(r'<style.*?</style>','',t,flags=re.S)
t=re.sub(r'<[^>]+>',' ',t)
t=html.unescape(t)
t=re.sub(r'[ \t]+',' ',t)
lines=[l.strip() for l in t.split('\n') if l.strip()]
print('\n'.join(lines[:120]))
