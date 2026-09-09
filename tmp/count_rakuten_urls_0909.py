# -*- coding: utf-8 -*-
"""登録に出てくる楽天の公演ページURL（deeplinkをほどいた素のURL）をユニークに数える。"""
import io, re, json, sys, urllib.parse, collections
sys.stdout.reconfigure(encoding='utf-8')

h = io.open('index.html', encoding='utf-8', newline='').read()
EV = json.loads(re.search(r'const EVENTS = (\[.*?\]);\r?\n', h, re.S).group(1))

def raw(u):
    if not u:
        return None
    if 'click.linksynergy.com' in u:
        m = re.search(r'murl=([^&]+)', u)
        if m:
            u = urllib.parse.unquote(m.group(1))
    return u if 'ticket.rakuten.co.jp' in u else None

urls = collections.OrderedDict()
for e in EV:
    for t in e.get('tickets') or []:
        u = raw(t.get('url'))
        if u:
            urls.setdefault(u, set()).add(e['id'])
    u = raw((e.get('links') or {}).get('rakuten'))
    if u:
        urls.setdefault(u, set()).add(e['id'])

print('楽天の公演ページ（ユニーク）= %d本' % len(urls))
print('関係するエントリ = %d件' % len({i for s in urls.values() for i in s}))
json.dump({u: sorted(v) for u, v in urls.items()},
          io.open('tmp/rakuten_urls_0909.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('→ tmp/rakuten_urls_0909.json')
