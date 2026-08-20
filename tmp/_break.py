import re,io,sys,datetime
p='C:/Users/user/oshinavi/index.html'
t=io.open(p,encoding='utf-8').read()
today=datetime.date.today().isoformat()
# "startDate": "今日" を持つ枠の直前の "date" を今日に書き換える
t,n=re.subn(r'"startDate": "'+today+r'",(\s*)"date": "\d{4}-\d{2}-\d{2}"', '"startDate": "'+today+r'",\1"date": "'+today+'"', t)
io.open(p,'w',encoding='utf-8').write(t)
print('隠れ枠に戻した', n, '枠')
