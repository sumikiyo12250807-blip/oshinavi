import io,json,re,sys
sys.stdout.reconfigure(encoding='utf-8')
t=io.open('C:/Users/user/oshinavi/index.html',encoding='utf-8',newline='').read()
m=re.search(r'const\s+EVENTS\s*=\s*(\[)',t)
ev,_=json.JSONDecoder().raw_decode(t,m.start(1))
json.dump(ev,open('events.json','w',encoding='utf-8'),ensure_ascii=False)
print(len(ev), max(e['id'] for e in ev))
