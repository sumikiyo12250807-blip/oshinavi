# -*- coding: utf-8 -*-
import json,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
d=json.load(open('tmp/parsed.json',encoding='utf-8'))
conv=[348,413,533,617,692,763,832,846,875,921,927,979,980,983,984,985,986,987,989,990,991,992,997,998,999,1000]
for i in conv:
    r=d[str(i)]
    print(f"\n=== id={i} ({d[str(i)]['url']}) ===")
    for row in r['rows']:
        if row['state'] in ('受付中','発売前'):
            print(f"  [{row['state']}|{row['stat_text']}] {row['pd']}~{row['pe']} {row['pref']} {row['venue'][:24]} | {row['title'][:34]} | {row['when']}")
