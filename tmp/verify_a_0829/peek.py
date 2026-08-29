import re,sys,os,html as H
D='C:/Users/user/oshinavi/tmp/verify_a_0829'
src=open(D+'/parse2.py',encoding='utf-8').read().split('man=json.load')[0]
g={}; exec(src,g)
files=sys.argv[1:]
out=[]
for f in files:
    p=D+'/raw/'+f
    h=open(p,encoding='utf-8',errors='replace').read()
    b=g['clean'](h)
    i=b.find('\u516c\u6f14\u65e5\u6642\u30fb\u5ea7\u5e2d')
    t=g['txt'](b[i:i+40000] if i>=0 else b)
    lines=[x.strip() for x in t.split('\n') if x.strip()]
    keep=[]
    for l in lines:
        if re.search(r'\d{4}/\d{1,2}/\d{1,2}\(', l) or '\u4f1a\u5834' in l or '\u958b\u6f14' in l or '\u5186' in l or '\u5e2d' in l or '\u5238' in l:
            keep.append(l)
    out.append('=== '+f+'\n'+'\n'.join(keep[:120]))
open(D+'/peek.txt','w',encoding='utf-8').write('\n\n'.join(out))
print('ok')
