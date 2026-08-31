# -*- coding: utf-8 -*-
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
ev = json.loads(re.search(r'const EVENTS = (\[.*?\]);\n', open('index.html.bak_0901_delete',encoding='utf-8').read(), re.S).group(1))
ids = [174,966,1078,1091,2265,2322,2537,2639,2666,3323,3401,4140,4808]
rows=[]
for e in ev:
    if e.get('id') in ids:
        l=e.get('links') or {}
        u = l.get('pia') or l.get('eplus') or l.get('rakuten') or l.get('lawson') or ''
        rows.append((e['id'], e.get('artist',''), e.get('venue',''), e.get('date',''), u))
rows.sort(key=lambda r: ids.index(r[0]))
out=["# 2026-09-01 朝の便で削除したエントリ（公演終了済 13件）","",
 "判定＝`date`（千秋楽）が 2026-09-01 より前で、未来日付の販売枠ゼロ。",
 "別エージェントに「削除は誤り」という前提でゼロから再導出させ、13件とも「削除してよい」で一致。",
 "全国ツアー型の 1091 / 2265 は念のため `reconcile_pia.py --ids` も通して**ぴあ側も0枠**を確認済み。","",
 "| id | 名前 | 会場 | 公演日 | 確認用URL |","|---|---|---|---|---|"]
for i,a,v,d,u in rows:
    out.append(f"| {i} | {a} | {v} | {d} | {u} |")
open('logs/removed_2026-09-01.md','w',encoding='utf-8').write("\n".join(out)+"\n")
print("\n".join(out))
