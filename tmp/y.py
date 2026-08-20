import re
h=open('tmp/eplus_kw1.html',encoding='utf-8',errors='replace').read()
o=open('tmp/y_out.txt','w',encoding='utf-8')
# find JSON-ish blobs
for m in re.finditer(r'\{[^{}]*"[^"]*(?:榛葉|パトナ|宮城野)[^"]*"[^{}]*\}', h):
    o.write(m.group(0)+"\n---\n")
o.write("\n\n##### detail links #####\n")
for m in set(re.findall(r'/sf/detail/\d+', h)):
    o.write(m+"\n")
o.write("\n##### dates near #####\n")
for m in re.finditer(r'(2026|2027)[/\-年]\s?\d{1,2}', h):
    pass
o.close()
