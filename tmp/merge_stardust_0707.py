# -*- coding: utf-8 -*-
"""スターダストレビュー全国ツアーの神奈川・山梨公演(2114)と新潟公演(2115)を統合。
一般発売とも7/25共通の同一全国ツアー。会場別eventCdをticket urlに付与。
彩の国くまがやドーム9/26公演(2047・発売7/18)は別公演なので触らない。
genre:new維持(振り分けはユーザー)。2115削除・NEW_ORDER除去。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DRY = '--apply' not in sys.argv
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
byid = {e['id']: e for e in EVENTS}
U_KANAGAWA = "https://t.pia.jp/pia/event/event.do?eventCd=2616460"
U_NIIGATA  = "https://t.pia.jp/pia/event/event.do?eventCd=2625797"
e = byid[2114]
e['date'] = "2026-10-18"
e['dateLabel'] = "2026年9月12日(土)〜10月18日(日) 全国ツアー（神奈川・山梨・新潟）"
e['venue'] = "全国ツアー"
e['prefecture'] = "全国"
e['tickets'] = [
 {"type":"3日先行（神奈川・山梨 9/12〜9/13公演）〜7/20 23:59","date":"2026-07-20","url":U_KANAGAWA},
 {"type":"一般発売（神奈川・山梨 9/12〜9/13公演）7/25 10:00発売","date":"2026-07-25","startDate":"2026-07-25","url":U_KANAGAWA},
 {"type":"先行（新潟 10/16〜10/18公演）〜7/13 11:00","date":"2026-07-13","url":U_NIIGATA},
 {"type":"一般発売（新潟 10/16〜10/18公演）7/25 10:00発売","date":"2026-07-25","startDate":"2026-07-25","url":U_NIIGATA},
]
DEL = {2115}
kept = [x for x in EVENTS if x.get('id') not in DEL]
print(f"merged 2115->2114 (tickets={len(e['tickets'])}); {len(EVENTS)}->{len(kept)}")
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
    open('index.html.bak_0707_stardust_merge','w',encoding='utf-8').write(h)
    open('index.html','w',encoding='utf-8').write(h2)
    print("written (backup: index.html.bak_0707_stardust_merge)")
