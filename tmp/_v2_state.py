import re, json, sys, os
sys.stdout.reconfigure(encoding='utf-8')
os.chdir(r'C:\Users\user\oshinavi')
h = open('index.html', encoding='utf-8', newline='').read()
ev = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
print("EVENTS件数:", len(ev))
raw = open('index.html','rb').read()
print("CRLF:", raw.count(b'\r\n'), "単独LF:", len(re.findall(rb'(?<!\r)\n', raw)))

so=[]; se=[]
for e in ev:
    for t in (e.get('tickets') or []):
        if t.get('soldout'): so.append((e['id'], t))
        if t.get('saleEnded'): se.append((e['id'], t))
print("\nsoldout枠:", len(so), " うち saleEnded枠:", len(se))
ids_so = sorted(set(i for i,_ in so)); ids_se = sorted(set(i for i,_ in se))
print("soldout持つエントリ:", len(ids_so), ids_so)
print("saleEnded持つエントリ:", len(ids_se), ids_se)
# saleEnded なのに soldout でないものは？
orphan = [(i,t) for i,t in se if not t.get('soldout')]
print("\nsaleEnded なのに soldout=false の枠:", len(orphan))
for i,t in orphan: print("   id%s %s" % (i, json.dumps(t,ensure_ascii=False)))

print("\n=== 全soldout枠一覧 ===")
byid={e['id']:e for e in ev}
for i,t in so:
    print("  id%-5s %-9s | %s | date=%s start=%s since=%s" % (
        i, '販売終了' if t.get('saleEnded') else '予定枚数終了', t.get('type'), t.get('date'), t.get('startDate'), t.get('soldoutSince')))

print("\n=== id1149 全体 ===")
print(json.dumps(byid[1149], ensure_ascii=False, indent=1))
