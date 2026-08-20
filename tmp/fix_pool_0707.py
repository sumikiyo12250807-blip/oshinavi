# -*- coding: utf-8 -*-
"""新着プールQC修正:
 ①星屑の会(2131): 先行〜7/13の取りこぼしを追加(ぴあ再取得結果)。
 ②トータルテンボス「ニコイチ」(2124): 熊本(2125)・宮城(2126)を同一ツアーとして統合、
   会場別eventCd券種付与、空カッコvenue解消。2125/2126削除・NEW_ORDER除去。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DRY = '--apply' not in sys.argv
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
byid = {e['id']: e for e in EVENTS}

# ① 星屑の会 先行追加
hoshi = json.load(open('tmp/built_hoshi.json', encoding='utf-8'))[0]
byid[2131]['tickets'] = hoshi['tickets']

# ② トータルテンボス統合
U_MAIN = "https://t.pia.jp/pia/event/event.do?eventCd=2624471"
U_KUMA = "https://t.pia.jp/pia/event/event.do?eventCd=2624149"
U_MIYA = "https://t.pia.jp/pia/event/event.do?eventCd=2625341"
e = byid[2124]
e['name'] = "トータルテンボス全国漫才ツアー2026「ニコイチ」"
e['artist'] = "トータルテンボス全国漫才ツアー2026「ニコイチ」"
e['venue'] = "全国ツアー"
e['prefecture'] = "全国"
e['date'] = "2026-12-06"
e['dateLabel'] = "2026年10月3日(土)〜12月6日(日) 全国ツアー"
e['tickets'] = [
 {"type":"一般発売（北海道・福島・新潟・福井・広島・香川・宮崎 10/3〜11/14公演）7/25 10:00発売","date":"2026-07-25","startDate":"2026-07-25","url":U_MAIN},
 {"type":"2次受付（熊本 11/20公演）〜7/9 11:00","date":"2026-07-09","url":U_KUMA},
 {"type":"一般発売（熊本 11/20公演）7/25 10:00発売","date":"2026-07-25","startDate":"2026-07-25","url":U_KUMA},
 {"type":"先行（宮城 12/6公演）〜7/13 11:00","date":"2026-07-13","url":U_MIYA},
 {"type":"一般発売（宮城 12/6公演）7/25 10:00発売","date":"2026-07-25","startDate":"2026-07-25","url":U_MIYA},
]
DEL = {2125,2126}
kept = [x for x in EVENTS if x.get('id') not in DEL]
print(f"星屑2131 tickets={len(byid[2131]['tickets'])}; トタテ統合 2125/2126削除; {len(EVENTS)}->{len(kept)}")
mo = re.search(r'(NEW_ORDER\s*=\s*)(\[[^\]]*\])', h)
order = json.loads(mo.group(2))
neworder = [i for i in order if i not in DEL]
print(f"NEW_ORDER {len(order)}->{len(neworder)}")
if DRY:
    print("(DRY)")
else:
    new_arr = json.dumps(kept, ensure_ascii=False, indent=2)
    h2 = h[:m.start()]+m.group(1)+new_arr+m.group(3)+h[m.end():]
    mo2 = re.search(r'(NEW_ORDER\s*=\s*)(\[[^\]]*\])', h2)
    h2 = h2[:mo2.start()]+mo2.group(1)+json.dumps(neworder)+h2[mo2.end():]
    open('index.html.bak_0707_pool_qc','w',encoding='utf-8').write(h)
    open('index.html','w',encoding='utf-8').write(h2)
    print("written (backup: index.html.bak_0707_pool_qc)")
