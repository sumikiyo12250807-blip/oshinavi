# -*- coding: utf-8 -*-
"""真打昇進披露興行4件(2085鈴本/2087末広亭/2088浅草/2089池袋)を id2085に統合。
都内4定席を順に回る同一興行・一般発売同7/21。会場別eventCdをticket urlに付与。
2087/2088/2089は削除、NEW_ORDERからも除去。genre=owarai確定。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DRY = '--apply' not in sys.argv
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
byid = {e['id']: e for e in EVENTS}

TICKETS = [
 {"type":"一般発売（鈴本演芸場 9/21〜9/30公演）7/21 10:00発売","date":"2026-07-21","startDate":"2026-07-21","url":"https://t.pia.jp/pia/event/event.do?eventCd=2615913"},
 {"type":"一般発売（新宿末広亭 10/1〜10/10公演）7/21 10:00発売","date":"2026-07-21","startDate":"2026-07-21","url":"https://t.pia.jp/pia/event/event.do?eventCd=2615915"},
 {"type":"一般発売（浅草演芸ホール 10/11〜10/20公演）7/21 10:00発売","date":"2026-07-21","startDate":"2026-07-21","url":"https://t.pia.jp/pia/event/event.do?eventCd=2615920"},
 {"type":"一般発売（池袋演芸場 10/21〜10/30公演）7/21 10:00発売","date":"2026-07-21","startDate":"2026-07-21","url":"https://t.pia.jp/pia/event/event.do?eventCd=2615923"},
]
e = byid[2085]
e['date'] = "2026-10-30"
e['dateLabel'] = "2026年9月21日(月)〜10月30日(金) 東京 鈴本演芸場・新宿末広亭・浅草演芸ホール・池袋演芸場"
e['venue'] = "鈴本演芸場・新宿末広亭・浅草演芸ホール・池袋演芸場"
e['genre'] = "owarai"
for k in ('_genre','_extraGenres','_piaSub'):
    e.pop(k, None)
e['tickets'] = TICKETS

DEL = {2087,2088,2089}
kept = [x for x in EVENTS if x.get('id') not in DEL]
print(f"merged into 2085 (tickets={len(e['tickets'])}), deleted {sorted(DEL)}; {len(EVENTS)}->{len(kept)}")

# NEW_ORDER除去
mo = re.search(r'(NEW_ORDER\s*=\s*)(\[[^\]]*\])', h)
order = json.loads(mo.group(2))
neworder = [i for i in order if i not in DEL]
print(f"NEW_ORDER {len(order)}->{len(neworder)}")

if DRY:
    print("(DRY)")
else:
    new_arr = json.dumps(kept, ensure_ascii=False, indent=2)
    h2 = h[:m.start()]+m.group(1)+new_arr+m.group(3)+h[m.end():]
    # NEW_ORDER置換(EVENTS書換後にhが変わるので再検索)
    mo2 = re.search(r'(NEW_ORDER\s*=\s*)(\[[^\]]*\])', h2)
    h2 = h2[:mo2.start()]+mo2.group(1)+json.dumps(neworder)+h2[mo2.end():]
    open('index.html.bak_0707_shinuchi_merge','w',encoding='utf-8').write(h)
    open('index.html','w',encoding='utf-8').write(h2)
    print("written (backup: index.html.bak_0707_shinuchi_merge)")
