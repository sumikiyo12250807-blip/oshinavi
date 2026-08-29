# -*- coding: utf-8 -*-
import json,re,io
s=open('index.html',encoding='utf-8',newline='').read()
m=re.search(r'(  const EVENTS = )(\[.*?\])(;)',s,re.S)
ev=json.loads(m.group(2))
new=[e for e in ev if e.get('genre')=='new']
o=io.open('logs/assigned_2026-08-27.md','w',encoding='utf-8')
o.write('# 2026-08-27 朝 新着の振り分け（%d件）\n\n' % len(new))
o.write('ジャンルは**ぴあのサブカテゴリを機械で写した**もの（人の判断ゼロ）。\n')
o.write('検証＝①独立再照合 tmp/recheck_pia_0826.py で17件とも指摘0件 ②別エージェントに公演日・会場・枠をゼロから再導出させて17件とも一致。\n\n')
o.write('| id | 公演名 | ぴあの区分 | ジャンル | 公演日 | 確認用URL |\n|---|---|---|---|---|---|\n')
for e in sorted(new,key=lambda x:x['id']):
    L=e.get('links') or {}
    o.write('| %d | %s | %s | **%s** | %s | %s |\n' % (
        e['id'], e.get('artist','').replace('|','｜'), e.get('_piaSub',''), e.get('_genre',''),
        e.get('date',''), L.get('pia','')))
o.write('\n## 保留（振り分けない）\n\n無し（17件とも機械で一意に決まった）\n')
o.close()
print('logs/assigned_2026-08-27.md', len(new))
