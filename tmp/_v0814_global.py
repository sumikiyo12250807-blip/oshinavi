import re, json, sys, os, collections
sys.stdout.reconfigure(encoding='utf-8')
os.chdir(r'C:\Users\user\oshinavi')
TODAY='2026-08-14'
h = open('index.html', encoding='utf-8', newline='').read()
ev = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
byid={e['id']:e for e in ev}

# 1. 締切 > 公演日
bad=[]
for e in ev:
    ed=e.get('date') or ''
    for t in (e.get('tickets') or []):
        d=t.get('date') or ''
        if d and ed and d>ed:
            bad.append((e['id'], e.get('artist'), ed, t.get('type'), d))
print("■ 販売終了日 > 公演日 の枠:", len(bad))
for b in bad[:30]: print("   ", b)

# 2. 本日ヒール15件の再点検（バッジ形式）
heal=[2789,3153,3316,3328,3598,3599,3699,3744,3825,3911,3927,3928,3929,3930]
print("\n■ 本日ヒール分のバッジ形式チェック")
for i in heal:
    e=byid[i]
    for t in e['tickets']:
        if t.get('startDate')==TODAY:
            m=re.search(r'（([^（）]+?)\s(\d{1,2}/\d{1,2}(?:〜\d{1,2}/\d{1,2})?)公演）', t['type'])
            print("   id%-5s %s | 県公演日=%s | date=%s 公演日=%s %s" % (i, t['type'][:60], (m.group(0) if m else '❌無し'), t['date'], e.get('date'), '⚠️締切>公演日' if t['date']>e['date'] else ''))

# 3. ぴあURL重複
d=collections.defaultdict(list)
for e in ev:
    u=(e.get('links') or {}).get('pia')
    if u: d[u].append(e['id'])
dup={u:v for u,v in d.items() if len(v)>1}
print("\n■ ぴあURL重複エントリ:", len(dup))
for u,v in list(dup.items())[:25]:
    print("   ", v, [ (byid[i].get('artist') or '')[:26] for i in v], u)

# 4. 今日が締切の枠 / 期限切れ枠が残ってないか
exp=[]
for e in ev:
    ts=e.get('tickets') or []
    alive=[t for t in ts if t.get('soldout') or (t.get('date') or '')>=TODAY or (t.get('startDate') and t['startDate']>=TODAY)]
    if not alive:
        exp.append((e['id'], e.get('artist'), e.get('date'), [t.get('date') for t in ts]))
print("\n■ 生き枠ゼロ（画面から消える）エントリ:", len(exp))
for x in exp[:40]: print("   ", x)
