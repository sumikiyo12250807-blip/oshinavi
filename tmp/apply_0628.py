# -*- coding: utf-8 -*-
"""6/28 発売前→販売中 変換を index.html に適用。
配列全体をパース→対象idのticketsをconvert_0628.jsonのfuture_ticketsに差し替え→
json.dumps(indent=2)で再dump(round-trip一致確認済)→const EVENTSブロックを丸ごと置換。"""
import re, json, io, sys, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
TODAY = '2026-06-28'

conv = json.load(open('tmp/convert_0628.json', encoding='utf-8'))
AUTO = [190,272,428,496,498,499,511,519,521,531,536,545,548,610,627,632,642,650,665,666,671,675,714,717,719,722,725,727,730,731,736,738,746,754,759,761,767,769,780,811,812,813,817,828,837,847,851,853,854,878,884,886,907,908,928,929,946,1020,1021,1024,1025,1026,1027,1028,1029,1030,1031,1032,1035,1036,1149,1150,1153,1167,1181,1183,1188,1193,1204,1205,1238,1243,1245,1253,1259,1265,1267,1294,1296,1297,1300,1305,1307,1308,1314,1316,1332,1344,1353,1366,1373,1377]
EXTRA = [406, 887]   # DROPだが本体は変換可(注記/別イベントのノイズdropのみ)
CONV_IDS = AUTO + EXTRA

# id1188 JUJU: bundleは全国ツアー・旧8公演は全て予定枚数終了→受付中は宮城9/26・9/27のみ(正)。
# ラベルが入れ子カッコで化けるので手動クリーン。
JUJU_TICKETS = [
    {'type': '一般発売（宮城 9/26公演）〜9/9 23:59', 'date': '2026-09-09'},
    {'type': '一般発売（宮城 9/27公演）〜9/9 23:59', 'date': '2026-09-09'},
]

def norm_ticket(t):
    """ファイル慣習の順 type, startDate, date, url に整える。"""
    d = {'type': t['type']}
    if t.get('startDate'): d['startDate'] = t['startDate']
    d['date'] = t['date']
    if t.get('url'): d['url'] = t['url']
    return d

txt = open('index.html', encoding='utf-8').read()
m = re.search(r'const EVENTS = (\[.*?\]);', txt, re.S)
arr = json.loads(m.group(1))
byid = {e['id']: e for e in arr}

applied, missing, empty = [], [], []
for eid in CONV_IDS:
    e = byid.get(eid)
    if not e: missing.append(eid); continue
    if eid == 1188:
        newt = [norm_ticket(t) for t in JUJU_TICKETS]
    else:
        fut = conv[str(eid)]['future_tickets']
        if not fut: empty.append(eid); continue
        newt = [norm_ticket(t) for t in fut]
    e['tickets'] = newt
    e['verifiedAt'] = TODAY
    applied.append(eid)

new_block = json.dumps(arr, ensure_ascii=False, indent=2)
new_txt = txt[:m.start(1)] + new_block + txt[m.end(1):]

print(f"適用 {len(applied)} / 対象 {len(CONV_IDS)}")
if missing: print("MISSING id:", missing)
if empty: print("EMPTY future_tickets:", empty)
shutil.copy('index.html', 'index.html.bak_0628_morning_convert')
open('index.html', 'w', encoding='utf-8').write(new_txt)
print("WROTE index.html (backup: index.html.bak_0628_morning_convert)")
