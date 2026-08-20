import re,json
h=open('tmp/eplus_kw1.html',encoding='utf-8',errors='replace').read()
m=re.search(r'<script id="json" class="json" type="application/json">\s*(\{.*?\})\s*</script>', h, re.S)
d=json.loads(m.group(1))
o=open('tmp/v_out.txt','w',encoding='utf-8')
recs=d['data']['record_list']
o.write("so_kensu=%s  recs=%d\n"%(d['data']['so_kensu'],len(recs)))
for r in recs:
    o.write("koenbi=%s venue=%s pref=%s kogyo=%s\n"%(r.get('koenbi_term'), (r.get('kanren_venue') or {}).get('venue_name'), (r.get('kanren_venue') or {}).get('todofuken_name'), r.get('kogyo_code')))
    for u in r.get('kanren_uketsuke_koen_list') or []:
        o.write("   sub=%s %s %s start=%s end=%s status=%s\n"%(u.get('kogyo_sub_code'),u.get('hambai_hoho_label'),u.get('uketsuke_name_pc'),u.get('uketsuke_start_datetime'),u.get('uketsuke_end_datetime'),u.get('uketsuke_status')))
o.close()
