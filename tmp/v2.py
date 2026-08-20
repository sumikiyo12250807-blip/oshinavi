import re,json
h=open('tmp/eplus_kw2.html',encoding='utf-8',errors='replace').read()
m=re.search(r'<script id="json" class="json" type="application/json">\s*(\{.*?\})\s*</script>', h, re.S)
o=open('tmp/v2_out.txt','w',encoding='utf-8')
if not m:
    o.write("NO JSON len=%d\n"%len(h))
else:
    d=json.loads(m.group(1)); recs=d['data']['record_list']
    o.write("so_kensu=%s recs=%d\n"%(d['data']['so_kensu'],len(recs)))
    for r in recs:
        v=r.get('kanren_venue') or {}
        o.write("%s | %s | %s | %s\n"%(r.get('koenbi_term'), v.get('venue_name'), v.get('todofuken_name'), (r.get('kanren_uketsuke_koen_list') or [{}])[0].get('shutsuensha')))
o.close()
