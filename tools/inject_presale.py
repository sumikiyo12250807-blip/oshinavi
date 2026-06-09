import re, json

src = open('index.html', encoding='utf-8').read()
recs = json.load(open('tmp/inject50.json', encoding='utf-8'))

PREF_SUFFIX = ('都', '府', '県')

def norm_pref(p):
    parts = re.split(r'[／/]', p)
    res = []
    for q in parts:
        q = q.strip()
        if q == '北海道':
            res.append('北海道')
        elif q.endswith(PREF_SUFFIX):
            res.append(q[:-1])
        else:
            res.append(q)
    return '／'.join(res)

def iso(d):
    y, m, dd = map(int, d.split('/'))
    return "%04d-%02d-%02d" % (y, m, dd)

def last_perf_iso(s):
    ds = re.findall(r'(\d{4})/(\d{1,2})/(\d{1,2})', s)
    ts = sorted((int(a), int(b), int(c)) for a, b, c in ds)
    y, m, d = ts[-1]
    return "%04d-%02d-%02d" % (y, m, d)

def clean_venue(v):
    return re.sub(r'\((?:北海道|[^()]{1,4}[都府県])\)', '', v).strip()

def datelabel(s):
    return re.sub(r'(\d{4})/(\d{1,2})/(\d{1,2})',
                  lambda m: "%s年%d月%d日" % (m.group(1), int(m.group(2)), int(m.group(3))),
                  s).strip()

def norm_url(u):
    m = re.search(r'eventCd=(\d+)', u)
    if m:
        return "https://t.pia.jp/pia/event/event.do?eventCd=" + m.group(1)
    m = re.search(r'eventBundleCd=(b\d+)', u)
    if m:
        return "https://t.pia.jp/pia/event/event.do?eventBundleCd=" + m.group(1)
    return u

def jd(s):
    return json.dumps(s, ensure_ascii=False)

objs = []
new_ids = []
nid = 501
for r in recs:
    artist = r['artist']
    name = artist if re.search(r'20(26|27)', artist) else artist + ' 2026'
    ev_date = last_perf_iso(r['perfdate'])
    sale = iso(r['rlsdate'])
    venue = clean_venue(r['venue'])
    pref = norm_pref(r['pref'])
    dl = datelabel(r['perfdate'])
    url = norm_url(r['url'])
    o = (
        '      {\n'
        '            "id": %d,\n' % nid +
        '            "artist": %s,\n' % jd(artist) +
        '            "name": %s,\n' % jd(name) +
        '            "date": %s,\n' % jd(ev_date) +
        '            "dateLabel": %s,\n' % jd(dl) +
        '            "venue": %s,\n' % jd(venue) +
        '            "prefecture": %s,\n' % jd(pref) +
        '            "genre": "new",\n'
        '            "price": null,\n'
        '            "links": {\n'
        '                  "rakuten": null,\n'
        '                  "lawson": null,\n'
        '                  "pia": %s,\n' % jd(url) +
        '                  "eplus": null\n'
        '            },\n'
        '            "tickets": [\n'
        '                  {\n'
        '                        "type": "一般発売",\n'
        '                        "startDate": %s,\n' % jd(sale) +
        '                        "date": %s\n' % jd(sale) +
        '                  }\n'
        '            ],\n'
        '            "showSalePeriod": true,\n'
        '            "verified": true,\n'
        '            "verifiedAt": "2026-06-09"\n'
        '      }'
    )
    objs.append(o)
    new_ids.append(nid)
    nid += 1

anchor = '      }\n      ];;;;;;;;'
assert src.count(anchor) == 1, 'anchor count=%d' % src.count(anchor)
block = '      },\n' + ',\n'.join(objs) + '\n      ];;;;;;;;'
src = src.replace(anchor, block)

no_new = '[' + ', '.join(str(i) for i in new_ids) + ']'
src, n = re.subn(r'(NEW_ORDER\s*=\s*\[)[0-9,\s]*(\])',
                 'NEW_ORDER = ' + no_new, src)
assert n == 1, 'NEW_ORDER replaced=%d' % n

open('index.html', 'w', encoding='utf-8').write(src)
print('inserted ids %d..%d (%d entries) | NEW_ORDER updated' % (new_ids[0], new_ids[-1], len(new_ids)))
