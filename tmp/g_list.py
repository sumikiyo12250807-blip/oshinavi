# -*- coding: utf-8 -*-
import json,os
BASE=r"C:/Users/user/oshinavi"
d=json.load(open(os.path.join(BASE,"tmp/g_extract.json"),encoding="utf-8"))
items=json.load(open(os.path.join(BASE,"tmp/genre_in_0825.json"),encoding="utf-8"))
lines=[]
for it in items:
    i=str(it["id"]); v=d[i]
    sub=v["sub"] or ("cd:"+",".join(v["genreCd"]))
    lines.append("%s | %s | %s | %s"%(i, sub, v["name"], v["url"]))
open(os.path.join(BASE,"tmp/g_list.txt"),"w",encoding="utf-8").write("\n".join(lines))
print("ok")
