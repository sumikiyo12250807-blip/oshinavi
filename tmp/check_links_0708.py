import re
ids = [323,334,436,510,1229,1285,1331,1459,1484,1531,1560,1571,1595,1607]
html = open('index.html', encoding='utf-8').read()
for i in ids:
    m = re.search(r'"id":\s*%d\s*,' % i, html)
    if not m:
        print(f"id={i}: NOT FOUND"); continue
    seg = html[m.start():m.start()+2500]
    lm = re.search(r'"links":\s*\{(.*?)\}', seg, re.S)
    linkstxt = lm.group(1) if lm else ""
    have = []
    for v in ['rakuten','lawson','pia','eplus','official']:
        vm = re.search(r'"%s":\s*("[^"]*"|null)' % v, linkstxt)
        if vm and vm.group(1) != 'null':
            have.append(v)
    print(f"id={i}: 実リンク有={have}")
