# e+新着の artist を「e+の出演欄に出ている全組」に直す（ユーザー選択A・2026-08-31）
# 出典＝各公演の e+ 実ページ <dt>出演</dt><dd>…</dd>（出演欄が無い2件はページタイトルの先頭）
import json,re,sys
sys.stdout.reconfigure(encoding='utf-8')
NEW={
 5989:'水上クリニック／My Lonely Vacation／ヒヨナリ／VERRE／SUGAR FORKFUL',
 5991:'黒蜜',
 5994:'マキナ',
 5995:'マキナ',
 5998:'フレデリック／This is LAST',
 5999:'パリパリ／ピカピカチューンズ!／もちもち／メロメロ',
 6001:'惡ノ夢',
 6002:'水上クリニック／シンギュラリティ／HUMAN ERROR／MeltyCΛlt／DAMILA',
 6005:'Ricky',
 6006:'透明少女',
 6008:'RENGEKI／【ベガ。】／My Lonely Vacation／水上クリニック／トリカブト／Lumieres／#どーぱみん／アザミ',
 6010:'ホタル／umbrella',
 6011:'MEME／THE DEVIL INSIDE／DLESS／蜈蚣／東海土下座組合',
 6012:'go!go!vanillas',
 6015:'LIL LEAGUE',
 6017:'羽多野渉／増田俊樹',
 6020:'ミーマイナー／niina／tight le fool／no more',
 6021:'おしゃぶり。／マキナ／THE_PiTY.／水上クリニック／あの子の部屋のカレンデュラは／TABOO／トリカブト／真夜中の続き',
 6023:'蛾と蝶',
}
path='index.html'
raw=open(path,encoding='utf-8',newline='').read()
m=re.search(r'(  const EVENTS = )(\[.*?\])(;)',raw,re.S)
ev=json.loads(m.group(2))
done=[]
for e in ev:
    if e['id'] in NEW:
        old=e.get('artist','')
        e['artist']=NEW[e['id']]
        done.append((e['id'],old,NEW[e['id']],e.get('name','')))
assert len(done)==len(NEW),(len(done),len(NEW))
body=json.dumps(ev,ensure_ascii=False,indent=2)
body='\n'.join('  '+l if l.strip() else l for l in body.split('\n')).lstrip()
out=raw[:m.start(2)]+body+raw[m.end(2):]
if '--apply' in sys.argv:
    open(path,'w',encoding='utf-8',newline='').write(out)
    print('書き込み完了')
for d in done: print(f'{d[0]}: 「{d[1]}」→「{d[2]}」')
