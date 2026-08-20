import json,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
d=json.load(open('tmp/parsed.json',encoding='utf-8'))
for i in [992,1000,979]:
    print(f"\n=== id={i} 全枠 ({d[str(i)]['url']}) ===")
    for row in d[str(i)]['rows']:
        print(f"  [{row['state']}|{row['stat_text']}] {row['pd']}~{row['pe']} {row['pref']} | {row['title'][:45]} | {row['when']}")
