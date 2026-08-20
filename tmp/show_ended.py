# -*- coding: utf-8 -*-
import json,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
d=json.load(open('tmp/parsed.json',encoding='utf-8'))
# 即終了が怪しいもの＋先行終了系
sus=[128,652,803,978,982,988,1129,434,468,658,438]
for i in sus:
    r=d[str(i)]
    print(f"\n===== id={i}  ({r.get('url')}) =====")
    for row in r['rows']:
        print(f"  [{row['state']}|{row['stat_text']}] {row['pd']}~{row['pe']} {row['pref']} {row['venue']} | {row['title'][:40]} | {row['when']}")
