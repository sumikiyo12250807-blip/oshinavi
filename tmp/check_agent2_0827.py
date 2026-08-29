# -*- coding: utf-8 -*-
import json,re,io,sys
sys.stdout.reconfigure(encoding='utf-8')
h=open('index.html',encoding='utf-8',newline='').read()
m=re.search(r'(  const EVENTS = )(\[.*?\])(;)',h,re.S)
EV={e['id']:e for e in json.loads(m.group(2))}
o=io.open('tmp/check_agent2_0827.md','w',encoding='utf-8')
for i,label in [(5391,'#10 ラ・カージュ'),(5394,'#13 グレンギャリー(sp形式URL)'),(5395,'#14 FOUR MINUTES'),
                (5396,'#15 清塚信也(予定枚数終了10枠)'),(5400,'#19 ロックンロール(sp形式URL)'),
                (5412,'#31 トスカ'),(5417,'#36 読響アンサンブル(10月が予定枚数終了)')]:
    e=EV.get(i)
    o.write('### id=%d %s\n'%(i,label))
    if not e: o.write('  (エントリなし)\n\n'); continue
    o.write('- artist=%s\n- date=%s pref=%s venue=%s\n- pia=%s\n'%(
        e.get('artist'),e.get('date'),e.get('prefecture'),e.get('venue'),(e.get('links') or {}).get('pia')))
    for t in e.get('tickets',[]):
        o.write('   * type=%s | date=%s | start=%s | soldout=%s | url=%s\n'%(
            t.get('type'),t.get('date'),t.get('startDate'),t.get('soldout'),t.get('url') or '(なし)'))
    o.write('\n')
# ticket.url が空の新着を全部数える
nourl=[e['id'] for e in EV.values() if 5332<=e['id']<=5431 and any(not t.get('url') for t in e.get('tickets',[]))]
o.write('## ticket.url が空の枠を持つ新着: %d件\n%s\n'%(len(nourl),nourl))
o.close()
print('ok', len(nourl))
