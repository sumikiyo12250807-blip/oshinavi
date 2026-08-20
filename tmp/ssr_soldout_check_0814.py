# -*- coding: utf-8 -*-
"""全枠soldoutのエントリが SSR(index.html の AI_SSR ブロック)と ai*.html に載っているか。
grepの文字化け誤判定を避けてPythonで照合する。"""
import re, json, sys, glob, datetime
sys.stdout.reconfigure(encoding='utf-8')

TODAY = datetime.date.today().isoformat()
h = open('index.html', encoding='utf-8').read()
evs = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))

ssr = h[h.index('<!-- AI_SSR_START -->'):h.index('<!-- AI_SSR_END -->')]
ai = ''
for f in sorted(glob.glob('ai*.html')):
    ai += open(f, encoding='utf-8').read()

allso = [e for e in evs
         if e.get('tickets') and all(t.get('soldout') for t in e['tickets'])
         and (e.get('date') or '9999') >= TODAY]
part = [e for e in evs
        if e.get('tickets') and any(t.get('soldout') for t in e['tickets'])
        and not all(t.get('soldout') for t in e['tickets'])]

def rep(label, lst):
    print(f'--- {label} ({len(lst)}件) ---')
    for e in lst:
        nm = e.get('name') or e.get('artist')
        print('id%-5s SSR=%-3s ai=%-3s verified=%-5s %s' % (
            e.get('id'), 'YES' if nm in ssr else 'NO',
            'YES' if nm in ai else 'NO', e.get('verified'), nm[:40]))

rep('全枠soldout', allso)
rep('一部soldout(生き枠あり)', part)
print('SSRのli数', ssr.count('<li>'), '/ EVENTS総数', len(evs),
      '/ verified=True', sum(1 for e in evs if e.get('verified') is True))
