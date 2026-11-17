# -*- coding: utf-8 -*-
import io, re, sys, html
sys.path.insert(0, 'C:/Users/user/oshinavi/tools')
import tiget_harvest as TH
h = TH.fetch('https://tiget.net/events/537107')
i = h.rfind('OP 13:00 / ST 13:30</p>')
seg = h[i:i + 3000]
seg = seg[:seg.find('来場チケット')]
names = [html.unescape(re.sub('<[^>]+>', '', x)).strip() for x in re.findall(r'<p[^>]*>(.*?)</p>', seg, re.S)]
io.open('C:/Users/user/oshinavi/tmp/x1117/spot/tiget50157_names.txt', 'w', encoding='utf-8').write('\n'.join(n for n in names if n))
