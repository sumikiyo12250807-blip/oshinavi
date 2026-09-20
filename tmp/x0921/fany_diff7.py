# -*- coding: utf-8 -*-
"""FANYの番人が鳴らした7件を調べる＝登録の枠がどの売り場のURLを持っているかを見る。
締切が食い違うのは「売り場ごとに締切が違う」だけなのか、それとも取り違えなのかを判断するため。
"""
import io, json, re, sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
IDS = [8761, 9250, 2417, 3269, 3316, 9420]

h = io.open('index.html', encoding='utf-8', newline='').read()
ev = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))}

out = io.open('tmp/x0921/fany_diff7.txt', 'w', encoding='utf-8')
for i in IDS:
    e = ev.get(i)
    if not e:
        out.write('id%s は見つからない\n\n' % i)
        continue
    out.write('=== id%s %s / %s @ %s（%s）公演%s\n'
              % (i, (e.get('artist') or '')[:30], (e.get('name') or '')[:40],
                 e.get('venue'), e.get('prefecture'), e.get('date')))
    out.write('  links: %s\n' % {k: v for k, v in (e.get('links') or {}).items() if v})
    for t in e.get('tickets') or []:
        u = t.get('url') or ''
        who = ('FANY' if 'fany.lol' in u else 'ぴあ' if 'pia.jp' in u
               else 'e+' if 'eplus' in u else '楽天' if 'rakuten' in u else 'その他')
        flags = ' '.join(k for k in ('soldout', 'saleEnded', 'presaleEnded', 'saleEndUnknown')
                         if t.get(k))
        out.write('  [%s] %s | date=%s %s\n      %s\n'
                  % (who, t.get('type'), t.get('date'), flags, u))
    out.write('\n')
out.close()
print('wrote tmp/x0921/fany_diff7.txt')
