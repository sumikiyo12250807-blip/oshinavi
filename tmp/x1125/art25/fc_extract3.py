import sys, json
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(open(r'C:/Users/user/oshinavi/tmp/x1125/art25/fc_yoko_3675json.txt.html', encoding='utf-8'))
out = []
for k in ('title', 'price', 'agency', 'ticket_sale_button', 'restriction'):
    out.append('## ' + k + '\n' + d.get(k, ''))
open(r'C:/Users/user/oshinavi/tmp/x1125/art25/fc_yoko_3675_raw.txt', 'w', encoding='utf-8').write('\n'.join(out))
