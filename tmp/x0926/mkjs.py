import io,json,sys
n,H,M=sys.argv[1],int(sys.argv[2]),int(sys.argv[3])
t=io.open(f'tmp/x0926/post{n}.txt',encoding='utf-8').read().replace('\r\n','\n')
mark=t.split('\n')[2][:12]
tpl=io.open('tmp/x0926/sched_tpl.js',encoding='utf-8').read()
js=tpl.replace('__T__',json.dumps(t)).replace('__H__',str(H)).replace('__M__',str(M)).replace('__MARK__',json.dumps(mark))
io.open(f'tmp/x0926/sched_{n}.js','w',encoding='utf-8').write(js)
sys.stdout.buffer.write(js.encode('ascii','backslashreplace'))
