# -*- coding: utf-8 -*-
import json,os,collections
BASE=r"C:/Users/user/oshinavi"
d=json.load(open(os.path.join(BASE,"tmp/g_extract.json"),encoding="utf-8"))
c=collections.Counter()
miss=[]
for i,v in d.items():
    if v["sub"]: c[v["sub"]]+=1
    else: miss.append((i,v["genreCd"],v["genreCdAny"],v["title"][:60]))
lines=[]
for k,n in c.most_common(): lines.append("%3d  %s"%(n,k))
lines.append("---- no sub in title: %d"%len(miss))
for m in miss: lines.append("%s  cd=%s any=%s  T=%s"%m)
open(os.path.join(BASE,"tmp/g_sum.txt"),"w",encoding="utf-8").write("\n".join(lines))
print("ok")
