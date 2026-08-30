# 名前の行だけをピンポイントで置換する（配列を作り直さない＝書式も改行も壊さない）
import json,re,sys
sys.stdout.reconfigure(encoding='utf-8')
NEW={
 5989:'水上クリニック／My Lonely Vacation／ヒヨナリ／VERRE／SUGAR FORKFUL',
 5991:'黒蜜', 5994:'マキナ', 5995:'マキナ',
 5998:'フレデリック／This is LAST',
 5999:'パリパリ／ピカピカチューンズ!／もちもち／メロメロ',
 6001:'惡ノ夢',
 6002:'水上クリニック／シンギュラリティ／HUMAN ERROR／MeltyCΛlt／DAMILA',
 6005:'Ricky', 6006:'透明少女',
 6008:'RENGEKI／【ベガ。】／My Lonely Vacation／水上クリニック／トリカブト／Lumieres／#どーぱみん／アザミ',
 6010:'ホタル／umbrella',
 6011:'MEME／THE DEVIL INSIDE／DLESS／蜈蚣／東海土下座組合',
 6012:'go!go!vanillas', 6015:'LIL LEAGUE',
 6017:'羽多野渉／増田俊樹',
 6020:'ミーマイナー／niina／tight le fool／no more',
 6021:'おしゃぶり。／マキナ／THE_PiTY.／水上クリニック／あの子の部屋のカレンデュラは／TABOO／トリカブト／真夜中の続き',
 6023:'蛾と蝶',
}
path='index.html'
lines=open(path,encoding='utf-8',newline='').read().split('\r\n')
cur=None; hits=[]
for i,ln in enumerate(lines):
    m=re.match(r'^\s*"id": (\d+),\s*$',ln)
    if m: cur=int(m.group(1)); continue
    if cur in NEW:
        m2=re.match(r'^(\s*"artist": )(".*")(,)\s*$',ln)
        if m2:
            old=json.loads(m2.group(2))
            lines[i]=m2.group(1)+json.dumps(NEW[cur],ensure_ascii=False)+m2.group(3)
            hits.append((cur,old,NEW[cur])); cur=None
assert len(hits)==len(NEW), (len(hits),len(NEW))
if '--apply' in sys.argv:
    open(path,'w',encoding='utf-8',newline='').write('\r\n'.join(lines))
    print('書き込み完了')
for h in hits: print(f'{h[0]}: 「{h[1]}」→「{h[2]}」')
