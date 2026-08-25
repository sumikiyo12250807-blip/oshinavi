# -*- coding: utf-8 -*-
import os,re,html as H
BASE=r"C:/Users/user/oshinavi"
ids=["5098","5119","5120","5122","5127","5131","5132","5156","5139","5197","5194","5100","5191","5126","5159"]
out=[]
for i in ids:
    raw=open(os.path.join(BASE,"tmp","g_%s.html"%i),"rb").read().decode("utf-8","replace")
    # strip scripts/styles
    t=re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>"," ",raw)
    t=re.sub(r"(?is)<[^>]+>"," ",t)
    t=H.unescape(t)
    t=re.sub(r"\s+"," ",t).strip()
    out.append("="*20+" "+i+" "+"="*20)
    out.append(t[:2200])
open(os.path.join(BASE,"tmp","g_detail.txt"),"w",encoding="utf-8").write("\n".join(out))
print("ok")
