import re,json
src=open('index.html',encoding='utf-8',newline='').read()
nl='\r\n' if '\r\n' in src else '\n'
text=src.replace('\r\n','\n')
m=re.search(r'=\s*(\[\s*\{.*?\}\s*\]);',text,re.S)
data=json.loads(m.group(1))
need=[e['id'] for e in data if e.get('genre')=='new' and e.get('verified')!=True]
lines=text.split('\n')
def find_span(eid):
    pat=re.compile(r'^\s*"id":\s*'+str(eid)+r'\s*,')
    idx=next((i for i,l in enumerate(lines) if pat.match(l)),None)
    if idx is None: return None
    s=idx
    while lines[s].strip()!='{': s-=1
    oi=len(lines[s])-len(lines[s].lstrip())
    e=idx
    while e<len(lines):
        st=lines[e].strip(); ind=len(lines[e])-len(lines[e].lstrip())
        if st in('}','},') and ind==oi and e>s: break
        e+=1
    return s,e
spans=[]
for eid in need:
    sp=find_span(eid)
    if sp: spans.append((sp[1],eid))   # closing line index
spans.sort(reverse=True)
cnt=0
for e,eid in spans:
    # line e-1 should be tickets close '    ]' ; add comma + verified lines before closing brace line e
    prev=e-1
    if lines[prev].strip()==']':
        lines[prev]=lines[prev]+','
        lines.insert(e, '    "verified": true,')
        lines.insert(e+1, '    "verifiedAt": "2026-06-19"')
        cnt+=1
    else:
        print('WARN unexpected prev for',eid,repr(lines[prev]))
open('index.html','w',encoding='utf-8',newline='').write('\n'.join(lines).replace('\n',nl))
print('verified付与:',cnt,'件')
