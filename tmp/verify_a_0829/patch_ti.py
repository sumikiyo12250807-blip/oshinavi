p='C:/Users/user/oshinavi/tmp/verify_a_0829/parse2.py'
s=open(p,encoding='utf-8').read()
old = (
    "    # performances table\n"
    "    perfs=[]\n"
    "    for m in re.finditer(r'itemprop=\"startDate\" datetime=\"([^\"]+)\"',b):\n"
    "        perfs.append(m.group(1)[:10])\n"
    "    o['perf_dates']=sorted(set(perfs))\n"
    "    vs=re.findall(r'\u4f1a\u5834\uff1a([^\\n<]{1,60})',txt(b))\n"
    "    o['venues']=sorted(set(v.strip() for v in vs))\n"
)
new = (
    "    sec=b\n"
    "    i=b.find('\u516c\u6f14\u65e5\u6642\u30fb\u5ea7\u5e2d')\n"
    "    if i>=0: sec=b[i:]\n"
    "    tt=re.sub(r'\\s+','',txt(sec))\n"
    "    PREF=r'(?:\u5317\u6d77\u9053|\u6771\u4eac\u90fd|\u5927\u962a\u5e9c|\u4eac\u90fd\u5e9c|.{2,4}\u770c)'\n"
    "    DATE=r'(\\d{4}/\\d{1,2}/\\d{1,2}\\([\u6708\u706b\u6c34\u6728\u91d1\u571f\u65e5]\\))'\n"
    "    o['perf_dates']=sorted(set(re.findall(DATE,tt)))\n"
    "    o['venues']=sorted(set(re.findall(r'\u4f1a\u5834\uff1a(.{1,40}?\\('+PREF+r'\\))',tt)))\n"
    "    o['perf_pairs']=re.findall(DATE+r'(?:(?!\\d{4}/\\d).){0,300}?\u4f1a\u5834\uff1a(.{1,40}?\\('+PREF+r'\\))',tt)[:80]\n"
)
assert old in s, 'no match'
open(p,'w',encoding='utf-8').write(s.replace(old,new))
print('patched')
