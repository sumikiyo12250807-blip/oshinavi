# -*- coding: utf-8 -*-
"""HEAD と比べて増えた枠のうち、ticket.url が空のものを出す（読むだけ）。
複数のぴあページを持つエントリで url が空だと、押した時にカードのリンク（別会場）へ飛んでしまう。"""
import json, re, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')


def load(t):
    return {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', t, re.S).group(1))}


old = load(subprocess.run(['git', 'show', 'HEAD:index.html'], capture_output=True).stdout.decode('utf-8', 'replace'))
new = load(open('index.html', encoding='utf-8').read())
n = 0
for i, e in new.items():
    o = old.get(i)
    if not o:
        continue
    had = {t.get('type') for t in o.get('tickets') or []}
    urls = {t.get('url') for t in e.get('tickets') or [] if t.get('url')} | {(e.get('links') or {}).get('pia')}
    urls.discard(None)
    for t in e.get('tickets') or []:
        if t.get('type') not in had and not t.get('url') and len(urls) > 1:
            n += 1
            print('id%s %s | %s | links.pia=%s' % (i, e.get('name')[:24], t.get('type'), (e.get('links') or {}).get('pia')))
print('url 空の新しい枠（複数ページのエントリ） %d' % n)
