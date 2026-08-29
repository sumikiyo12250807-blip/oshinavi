# -*- coding: utf-8 -*-
import json,sys,io,re
sys.stdout.reconfigure(encoding='utf-8')
def fmt(s):
    if not s: return ''
    s=str(s)
    if len(s)>=8:
        r='%s-%s-%s'%(s[0:4],s[4:6],s[6:8])
        if len(s)>=12: r+=' %s:%s'%(s[8:10],s[10:12])
        return r
    return s
for p,name in [('tmp/ep_takaiwa.json','高岩遼'),('tmp/ep_akuruyo.json','明くる夜の羊')]:
    d=json.load(open(p,encoding='utf-8'))
    o=io.open('tmp/ep_%s.md'%('takaiwa' if 'takaiwa' in p else 'akuruyo'),'w',encoding='utf-8')
    o.write('# e+ 検索結果: %s\n\n'%name)
    recs=[]
    def walk(x):
        if isinstance(x,dict):
            if 'record_list' in x and isinstance(x['record_list'],list):
                recs.extend(x['record_list'])
            for v in x.values(): walk(v)
        elif isinstance(x,list):
            for v in x: walk(v)
    walk(d)
    o.write('件数 %d\n\n'%len(recs))
    for r in recs:
        v=r.get('kanren_venue') or {}
        o.write('## %s\n'%(r.get('kogyo_name') or r.get('kogyo_sub_name') or '(名称キー不明)'))
        o.write('- 全キー: %s\n'%', '.join(sorted(k for k in r.keys() if not isinstance(r[k],(dict,list)))))
        o.write('- 公演日: %s / 開演 %s\n'%(fmt(r.get('koenbi_term')), r.get('kaien_time')))
        o.write('- 会場: %s (%s)\n'%(v.get('venue_name'),v.get('todofuken_name')))
        o.write('- kogyo_code: %s\n'%r.get('kogyo_code'))
        for u in (r.get('kanren_uketsuke_koen_list') or []):
            o.write('   * %s [%s] status=%s 受付 %s 〜 %s\n'%(
                u.get('uketsuke_name_pc'),u.get('hambai_hoho_label'),u.get('uketsuke_status'),
                fmt(u.get('uketsuke_start_datetime')),fmt(u.get('uketsuke_end_datetime'))))
        o.write('\n')
    o.close()
    print(name,'records',len(recs))
