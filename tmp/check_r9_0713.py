# -*- coding: utf-8 -*-
"""新着の2027年公演がバッジで「R9年」表記になっているか確認（feedback_r9_year_notation）。
公演日が2027以降 or dateLabel/ticket.type に 2027 を含むものを洗う。"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
E = json.loads(m.group(2))
NEW = [e for e in E if e.get('genre') == 'new']

hit = [e for e in NEW if (e.get('date', '') >= '2027') or '2027' in (e.get('dateLabel') or '')]
print(f'=== 新着で2027年に関わる公演 {len(hit)}件 ===')
for e in hit:
    print(f"\nid{e['id']} {e.get('artist','')}")
    print(f"   date={e.get('date')} / dateLabel={e.get('dateLabel')}")
    for t in e.get('tickets', []):
        tp = t.get('type', '')
        flag = 'OK' if ('R9' in tp or 'R9' in (t.get('dateLabel') or '')) else '⚠️R9表記なし'
        print(f"   [{flag}] {tp} | date={t.get('date')} start={t.get('startDate')}")
