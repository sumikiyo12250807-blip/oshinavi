import re,json,sys
h=open('tmp/eplus_kw1.html',encoding='utf-8',errors='replace').read()
out=open('tmp/x_out.txt','w',encoding='utf-8')
for m in re.finditer(r'榛葉樹人', h):
    i=m.start()
    out.write("=== at %d ===\n"%i)
    out.write(h[max(0,i-2500):i+2500].replace('\xa0',' '))
    out.write("\n\n")
out.close()
