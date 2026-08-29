# -*- coding: utf-8 -*-
import json,re,io,sys
sys.stdout.reconfigure(encoding='utf-8')
h=open('index.html',encoding='utf-8',newline='').read()
m=re.search(r'(  const EVENTS = )(\[.*?\])(;)',h,re.S)
EV={e['id']:e for e in json.loads(m.group(2))}
o=io.open('tmp/check_agent1_0827.md','w',encoding='utf-8')
# agentlist_1 は id 5332..5381（番号N → id 5331+N）
for n,label in [(8,'木村カエラ 広島11/1は枠0・東京2/5だけ'),(14,'浪漫革命 4枠'),(19,'絆コンサート 同日2公演'),
                (23,'宮本佳林 同日2回公演'),(25,"OKAMOTO'S 先行13公演/一般3公演のみ"),(31,'TRIPLANE 2会場・発売10/25 21:00'),
                (36,'岡村靖幸 埼玉2/21+千葉2/28'),(40,'TAGRIGHT 発売日が枠ごとに違う'),
                (42,'動画配信 吹奏楽'),(44,'あきつ落語会 近日抽選受付'),(45,'熊川哲也K-BALLET 13公演')]:
    i=5331+n; e=EV.get(i)
    o.write('### #%d → id=%d  %s\n'%(n,i,label))
    if not e: o.write('  (なし)\n\n'); continue
    o.write('- artist=%s\n- date=%s pref=%s\n- venue=%s\n- pia=%s\n'%(
        e.get('artist'),e.get('date'),e.get('prefecture'),e.get('venue'),(e.get('links') or {}).get('pia')))
    for t in e.get('tickets',[]):
        o.write('   * %s | date=%s start=%s\n'%(t.get('type'),t.get('date'),t.get('startDate')))
    o.write('\n')
o.close()
print('ok')
