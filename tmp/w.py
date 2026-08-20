import re
h=open('tmp/eplus_kw1.html',encoding='utf-8',errors='replace').read()
o=open('tmp/w_out.txt','w',encoding='utf-8')
i=h.find('349942')
while i>0:
    o.write("=== %d ===\n"%i)
    o.write(h[max(0,i-3000):i+1500].replace('\xa0',' ')+"\n\n")
    i=h.find('349942', i+1)
    if i>60000: break
o.close()
