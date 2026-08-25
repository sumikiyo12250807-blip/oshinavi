# -*- coding: utf-8 -*-
import re,sys,html
sys.stdout.reconfigure(encoding="utf-8")
for path in sys.argv[1:]:
    h=open(path,encoding="utf-8",errors="replace").read()
    h=re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>',' ',h)
    t=html.unescape(re.sub(r'<[^>]+>','\n',h))
    t=re.sub(r'\n\s*','\n',t)
    t=re.sub(r'\n+','\n',t)
    # rejoin date like 2026/10/18(\n日\n)
    t=re.sub(r'(\d{4}/\d{1,2}/\d{1,2})\(\n([^\n]{1,4})\n\)', r'\1(\2)', t)
    print("="*70); print(path)
    lines=t.split('\n')
    out=[]
    for i,l in enumerate(lines):
        if re.match(r'^\d{4}/\d{1,2}/\d{1,2}\(', l):
            nxt=[x for x in lines[i+1:i+5]]
            ven=[x for x in nxt if x.startswith('会場：')]
            tm=[x for x in nxt if '開演' in x]
            out.append((l, tm[0] if tm else '', ven[0] if ven else ''))
    seen=set(); n=0
    for o in out:
        if o in seen: continue
        seen.add(o); n+=1
        print("  %2d %s | %s | %s"%(n,o[0],o[1],o[2]))
