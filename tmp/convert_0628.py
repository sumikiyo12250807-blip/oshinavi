# -*- coding: utf-8 -*-
"""6/28朝 期限切れ変換: 6/27発売開始の発売前→販売中。
build_pia_entries の parse_cards/parse_when/正規化を再利用(canonicalパーサーに自動追従)。
各idのぴあURL群を機械パースし、現在「受付中/発売前」の券種から販売中ticketsを再導出する。
分類:
  AUTO  = 買える券種が取れた → tickets差し替え案
  SOLD  = 買える券種ゼロ → 売切/終了の疑い(削除候補・要WebFetch)
  DROP  = parse_whenで日付解析不能の枠あり → 手動確認
"""
import re, json, io, sys, time, importlib.util, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
spec = importlib.util.spec_from_file_location('bpe', 'tools/build_pia_entries.py')
bpe = importlib.util.module_from_spec(spec); spec.loader.exec_module(bpe)

IDS = [43,64,147,190,272,273,368,406,417,428,469,480,493,496,498,499,511,519,521,531,536,545,548,604,610,627,632,642,648,650,665,666,671,675,714,717,719,722,725,727,730,731,736,738,743,746,754,769,780,759,760,761,767,811,812,813,817,828,837,847,851,853,854,878,881,884,886,887,907,908,928,929,946,1020,1021,1024,1025,1026,1027,1028,1029,1030,1031,1032,1033,1034,1035,1036,1149,1150,1153,1167,1181,1183,1188,1193,1204,1205,1238,1243,1245,1253,1259,1265,1267,1294,1296,1297,1300,1305,1307,1308,1314,1316,1329,1332,1343,1344,1348,1353,1355,1356,1366,1369,1373,1377]
# 公演終了済(削除候補・別枠)も実態確認のため含める
HARD_DEL = [106,168,395,401,1289]

h = open('index.html', encoding='utf-8').read()
m = re.search(r'const EVENTS\s*=\s*(\[.*?\]);', h, re.S)
arr = json.loads(m.group(1)); byid = {e['id']: e for e in arr}

def pia_urls(ev):
    urls = []
    p = (ev.get('links') or {}).get('pia')
    if p and 'pia' in p: urls.append(p)
    for t in ev.get('tickets', []):
        u = t.get('url')
        if u and 'pia' in u and u not in urls: urls.append(u)
    return urls

def build_tickets(urls):
    allrows, drops = [], []
    for u in urls:
        try:
            hh = bpe.fetch(u)
            su = bpe.src_event_url(u)
            for c in bpe.parse_cards(hh):
                c['_src'] = su; allrows.append(c)
            time.sleep(0.25)
        except Exception as ex:
            drops.append(('FETCH', str(ex)[:60], u))
    buy = [r for r in allrows if r['state'] in ('受付中', '発売前')]
    seen, rows = set(), []
    for r in buy:
        k = (r['perfdate'], r['perf_end'], r['venue'], r['title'], r['state'])
        if k in seen: continue
        seen.add(k); rows.append(r)
    srcs = set(r.get('_src') for r in rows if r.get('_src'))
    multi = len(srcs) > 1
    tickets = []
    for r in rows:
        suf, iso, sd = bpe.parse_when(r['state'], r['when'])
        if not iso:
            drops.append(('WHEN', r.get('state'), r.get('when',''), r.get('title','')[:40])); continue
        pe = r.get('perf_end') or r['perfdate']
        mdr = bpe.md(r['perfdate']) if pe == r['perfdate'] else f"{bpe.md(r['perfdate'])}〜{bpe.md(pe)}"
        pf = '・'.join(r['prefs']) if r['prefs'] else '全国'
        t = {'type': bpe.norm_fw(f"{bpe.kenshu(r['title'])}（{pf} {mdr}公演）{suf}"), 'date': iso}
        if sd: t['startDate'] = sd
        if multi:
            tu = bpe.ecd_url(r['url']) or r.get('_src')
            if tu: t['url'] = tu
        tickets.append(t)
    tickets.sort(key=lambda t: t['date'])
    return tickets, drops

out = {}
allids = IDS + HARD_DEL
for n, eid in enumerate(allids, 1):
    e = byid.get(eid)
    if not e:
        sys.stderr.write(f'[{n}] id{eid} NOT FOUND\n'); continue
    urls = pia_urls(e)
    tickets, drops = build_tickets(urls)
    fut = [t for t in tickets if t['date'] >= bpe.datetime.date.today().isoformat()]
    rec = {'name': e['name'][:48], 'perf_date': e.get('date'), 'urls': urls,
           'new_tickets': tickets, 'future_tickets': fut, 'drops': drops,
           'hard_del': eid in HARD_DEL}
    if drops and any(d[0]=='WHEN' for d in drops): rec['cat'] = 'DROP'
    elif not fut: rec['cat'] = 'SOLD'
    else: rec['cat'] = 'AUTO'
    out[eid] = rec
    sys.stderr.write(f'[{n}/{len(allids)}] id{eid} {rec["cat"]} ({len(fut)}枠)\n'); sys.stderr.flush()

json.dump(out, open('tmp/convert_0628.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
cats = {}
for eid, r in out.items(): cats.setdefault(r['cat'], []).append(eid)
print("\n===== 分類サマリー =====")
for k in ('AUTO','SOLD','DROP'):
    print(f"{k}: {len(cats.get(k,[]))}件  {cats.get(k,[])}")
print("\nWROTE tmp/convert_0628.json")
