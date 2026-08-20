# -*- coding: utf-8 -*-
"""6/20発売開始の発売前エントリ96件について、ぴあページを機械パースして
現在「受付中」の券種とその終了日(when)を取得し、変換案JSONを出力する。
WebFetch要約は使わない（feedback_webfetch_soldout_false_positive）。"""
import json, re, io, sys, time, urllib.request, html as _html
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

IDS = [334,401,416,497,503,506,515,516,518,527,528,538,541,542,547,617,631,640,651,
664,670,673,679,687,691,698,707,709,720,732,739,745,763,785,787,802,808,809,810,816,
818,831,834,840,852,855,858,862,870,872,880,883,891,894,897,899,900,925,930,933,936,
937,938,939,941,943,944,945,947,948,949,951,952,953,954,956,957,958,959,960,961,962,
963,964,965,967,968,969,970,971,972,973,974,975,976,977]

txt = open('index.html', encoding='utf-8').read()
i = txt.index('const EVENTS = [') + len('const EVENTS = ')
arr, _ = json.JSONDecoder().raw_decode(txt, i)
byid = {e['id']: e for e in arr}

def fetch(u):
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')

def clean(s):
    return _html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s or ''))).strip()

def parse_cards(h):
    items = re.split(r'(?=<li class="ticketSalesList-2024__item)', h)
    rows = []
    for it in items:
        if 'ticketSalesCard-2024__status' not in it:
            continue
        m_title = re.search(r'__title">(.*?)</p>', it, re.S)
        m_place = re.search(r'__place"[^>]*>(.*?)</span>', it, re.S)
        m_region = re.search(r'__region">(.*?)</span>', it, re.S)
        _dts = re.findall(r'datetime="(\d{4}-\d{2}-\d{2})', it)
        m_stat = re.search(r'__status (is-\w+)">(.*?)(?:<br|</p>)', it, re.S)
        m_sdate = re.search(r'__status[^>]*>.*?<br>\s*<span[^>]*>(.*?)</span>', it, re.S)
        stat_text = clean(m_stat.group(2)) if m_stat else ''
        sdate = clean(m_sdate.group(1)) if m_sdate else ''
        if re.search(r'(販売期間中|受付中)', stat_text): state = '受付中'
        elif '発売前' in stat_text: state = '発売前'
        else: state = '受付終了'
        rows.append({
            'perf': _dts[0] if _dts else '', 'perf_end': _dts[-1] if _dts else '',
            'venue': clean(m_place.group(1)) if m_place else '',
            'pref': clean(m_region.group(1)) if m_region else '',
            'title': clean(m_title.group(1)) if m_title else '',
            'state': state, 'when': sdate,
        })
    seen=set(); uniq=[]
    for r in rows:
        k=(r['perf'],r['perf_end'],r['venue'],r['title'],r['state'],r['when'])
        if k in seen: continue
        seen.add(k); uniq.append(r)
    return uniq

out = {}
for n, eid in enumerate(IDS, 1):
    e = byid[eid]
    pia = (e.get('links') or {}).get('pia') or ''
    rec = {'name': e['name'][:50], 'perf_date': e['date'], 'pia': pia,
           'cur_tickets': [{'type': t['type'], 'date': t.get('date'),
                            'startDate': t.get('startDate'),
                            'sus': t.get('saleUntilSoldOut')} for t in e['tickets']]}
    try:
        h = fetch(pia)
        cards = parse_cards(h)
        rec['uketsuke'] = [c for c in cards if c['state']=='受付前' or c['state']=='受付中' or c['state']=='発売前']
        rec['all_states'] = sorted(set(c['state'] for c in cards))
    except Exception as ex:
        rec['error'] = str(ex)
    out[eid] = rec
    sys.stderr.write(f'[{n}/{len(IDS)}] id{eid} done\n'); sys.stderr.flush()
    time.sleep(0.4)

json.dump(out, open('tmp/presale_ends.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('WROTE tmp/presale_ends.json with', len(out), 'entries')
