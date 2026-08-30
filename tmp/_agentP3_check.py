# -*- coding: utf-8 -*-
import urllib.request, re, io, sys, html as _html, json, time, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class PiaSorry(Exception): pass

def fetch(u):
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=40) as r:
        final = r.geturl()
        body = r.read().decode('utf-8', 'replace')
    if 'sorry.pia' in final or 'sorry.pia' in body[:4000]:
        raise PiaSorry('sorry page')
    return body

def txt(s):
    return _html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s or ''))).strip()

def parse(h):
    items = re.split(r'(?=<li class="ticketSalesList-2024__item)', h)
    rows = []
    for it in items:
        if 'ticketSalesCard-2024__status' not in it: continue
        m_url = re.search(r'href="(https://t\.pia\.jp/pia/ticketInformation\.do\?[^"]+)"', it)
        m_title = re.search(r'__title">(.*?)</p>', it, re.S)
        m_place = re.search(r'__place"[^>]*>(.*?)</span>', it, re.S)
        m_region = re.search(r'__region">(.*?)</span>', it, re.S)
        _dts = re.findall(r'datetime="(\d{4}-\d{2}-\d{2})', it)
        perf_start = _dts[0] if _dts else ''
        perf_end = _dts[-1] if _dts else ''
        m_stat = re.search(r'__status (is-[\w-]+)">(.*?)(?:<br|</p>)', it, re.S)
        m_sdate = re.search(r'__status[^>]*>.*?<br>\s*<span[^>]*>(.*?)</span>', it, re.S)
        stat_text = txt(m_stat.group(2)) if m_stat else ''
        cls = m_stat.group(1) if m_stat else ''
        sdate = txt(m_sdate.group(1)) if m_sdate else ''
        if re.search(r'(予定枚数|完売|売り?切|受付は?終了|販売終了|販売期間終了|終了しました|結果発表)', stat_text):
            state = '受付終了'
        elif cls == 'is-active' or re.search(r'(販売期間中|受付中|発売中|販売中|発売初日|本日発売)', stat_text):
            state = '受付中'
        elif cls == 'is-before' or '発売前' in stat_text or 'まもなく' in stat_text:
            state = '発売前'
        else:
            state = '受付終了'
        rows.append(dict(perfdate=perf_start, perf_end=perf_end, statustext=stat_text,
                         venue=txt(m_place.group(1)) if m_place else '',
                         pref=txt(m_region.group(1)) if m_region else '',
                         title=txt(m_title.group(1)) if m_title else '',
                         state=state, when=sdate, url=m_url.group(1) if m_url else ''))
    seen=set(); uniq=[]
    for r in rows:
        k=(r['perfdate'],r['perf_end'],r['venue'],r['title'],r['state'],r['when'],r['url'])
        if k in seen: continue
        seen.add(k); uniq.append(r)
    return uniq

def page_meta(h):
    t = re.search(r'<title>(.*?)</title>', h, re.S)
    t = _html.unescape(t.group(1).strip()) if t else ''
    g = re.search(r'チケットぴあ\[(.*?)のチケット', t)
    genre = g.group(1) if g else ''
    name = t.split(' | ')[0].strip() if ' | ' in t else t
    bc = re.search(r'breadCrumb-2024".*?</ul>', h, re.S)
    crumbs = [txt(x) for x in re.findall(r'breadCrumb-2024__item[^>]*>(.*?)</li>', bc.group(0), re.S)] if bc else []
    return name, genre, crumbs

lines = [l.rstrip('\n') for l in open('tmp/_poolgrp3_0831.txt', encoding='utf-8') if l.strip()]
out = []
for idx, l in enumerate(lines):
    parts = l.split('|')
    # name may contain '|' -> id is parts[0], last 5 fields fixed from the end
    eid = parts[0]; url = parts[-1]; cnt = parts[-2]; pref = parts[-3]; date = parts[-4]
    name = '|'.join(parts[1:-4])
    rec = dict(id=eid, reg_name=name, reg_date=date, reg_pref=pref, reg_cnt=cnt, url=url)
    got = None
    for attempt in range(4):
        try:
            h = fetch(url)
            rows = parse(h)
            buy = [r for r in rows if r['state'] in ('受付中','発売前')]
            if len(rows) == 0 and attempt < 3:
                time.sleep(6); continue
            got = (h, rows, buy); break
        except PiaSorry as e:
            rec.setdefault('errs',[]).append('sorry'); time.sleep(8)
        except Exception as e:
            rec.setdefault('errs',[]).append(type(e).__name__+':'+str(e)[:80]); time.sleep(6)
    if got is None:
        rec['status']='FETCH_FAIL'
    else:
        h, rows, buy = got
        nm, genre, crumbs = page_meta(h)
        alld = sorted({r['perf_end'] or r['perfdate'] for r in rows if r['perfdate']})
        buyd = sorted({r['perf_end'] or r['perfdate'] for r in buy if r['perfdate']})
        rec.update(status='OK', pia_name=nm, genre=genre, crumbs=crumbs,
                   n_all=len(rows), n_buy=len(buy),
                   n_active=len([r for r in rows if r['state']=='受付中']),
                   n_before=len([r for r in rows if r['state']=='発売前']),
                   n_end=len([r for r in rows if r['state']=='受付終了']),
                   maxdate_all=alld[-1] if alld else '', maxdate_buy=buyd[-1] if buyd else '',
                   prefs_buy=sorted({r['pref'] for r in buy if r['pref']}),
                   prefs_all=sorted({r['pref'] for r in rows if r['pref']}),
                   cards=[{k:r[k] for k in ('state','statustext','perfdate','perf_end','pref','venue','title','when')} for r in rows])
    out.append(rec)
    print(f"[{idx+1}/{len(lines)}] {eid} {rec.get('status')} buy={rec.get('n_buy')} all={rec.get('n_all')}", flush=True)
    time.sleep(1.2)

json.dump(out, open('tmp/_agentP3_result.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('DONE')
