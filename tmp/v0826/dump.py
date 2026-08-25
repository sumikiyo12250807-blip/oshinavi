# -*- coding: utf-8 -*-
import re,sys,html
sys.stdout.reconfigure(encoding="utf-8")
for path in sys.argv[1:]:
    h=open(path,encoding="utf-8",errors="replace").read()
    h=re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>',' ',h)
    t=html.unescape(re.sub(r'<[^>]+>','\n',h))
    lines=[l.strip() for l in t.split('\n') if l.strip()]
    # cut noise
    try: s=max(i for i,l in enumerate(lines) if l=='チケット情報')
    except ValueError: s=0
    try: e=min(i for i,l in enumerate(lines) if l=='アイコン説明')
    except ValueError: e=len(lines)
    print("="*70); print(path)
    print("TITLE:", lines[0] if lines else '')
    print("\n".join(lines[s:e]))
