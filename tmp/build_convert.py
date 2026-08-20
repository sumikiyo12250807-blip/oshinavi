# -*- coding: utf-8 -*-
"""presale_ends.json から変換案を組む。
各エントリの現発売前ticketを、ぴあ受付中券種の終了日(when)で販売中形に変換。
分類:
  AUTO  = 受付中券種があり終了日が取れる → 自動変換案
  SOLD  = 受付中ゼロ(全て受付終了/予定枚数終了) → 売切/終了の疑い・要確認
  PRE   = まだ発売前state(発売開始してない=誤フラグ) → 据え置き
  MULTI = 受付中が複数で終了日バラバラ → 手動確認
"""
import json, re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
d = json.load(open('tmp/presale_ends.json', encoding='utf-8'))

def when_to_date(w):
    # "～ 2026/9/10(木) 23:59" -> ("2026-09-10","23:59","9/10")
    m = re.search(r'(\d{4})/(\d{1,2})/(\d{1,2}).*?(\d{1,2}:\d{2})', w)
    if not m:
        m2 = re.search(r'(\d{4})/(\d{1,2})/(\d{1,2})', w)
        if not m2: return None
        y,mo,da = m2.group(1),int(m2.group(2)),int(m2.group(3))
        return (f'{y}-{mo:02d}-{da:02d}', '23:59', f'{mo}/{da}')
    y,mo,da,hm = m.group(1),int(m.group(2)),int(m.group(3)),m.group(4)
    return (f'{y}-{mo:02d}-{da:02d}', hm, f'{mo}/{da}')

cats = {'AUTO':[], 'SOLD':[], 'PRE':[], 'MULTI':[], 'ERR':[]}
for eid, rec in d.items():
    if 'error' in rec: cats['ERR'].append(eid); continue
    uk = rec.get('uketsuke', [])
    uketsuke_now = [c for c in uk if c['state']=='受付中']
    presale = [c for c in uk if c['state']=='発売前']
    # 一般発売/プリセール系の受付中だけ拾う(先行抽選は別)
    gen = [c for c in uketsuke_now if ('一般' in c['title'] or 'プリセール' in c['title'] or '一般' in c['title'])]
    if not uketsuke_now and presale:
        cats['PRE'].append(eid)
    elif not uketsuke_now:
        cats['SOLD'].append(eid)
    else:
        ends = set()
        for c in uketsuke_now:
            wd = when_to_date(c['when'])
            if wd: ends.add(wd[0])
        if len(ends) <= 1:
            cats['AUTO'].append(eid)
        else:
            cats['MULTI'].append(eid)

for k in ['AUTO','MULTI','SOLD','PRE','ERR']:
    print(f"\n===== {k} ({len(cats[k])}) =====")
    for eid in cats[k]:
        rec=d[eid]
        uk=[c for c in rec.get('uketsuke',[]) if c['state']=='受付中']
        ends=sorted(set(c['when'] for c in uk))
        print(f"  id{eid} {rec['name']} | states={rec.get('all_states')} | 受付中{len(uk)} ends={ends}")
json.dump(cats, open('tmp/convert_cats.json','w',encoding='utf-8'), ensure_ascii=False)
