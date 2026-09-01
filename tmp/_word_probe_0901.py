# -*- coding: utf-8 -*-
import sys, re, html as H
sys.path.insert(0,'tools'); sys.stdout.reconfigure(encoding='utf-8')
from eplus_harvest import fetch
h = fetch('https://eplus.jp/sf/word/0000168060')
print('bytes', len(h))
t = (re.search(r'<title>(.*?)</title>', h, re.S) or [None,''])[1]
print('TITLE:', H.unescape(t)[:200])
urls = sorted(set(re.findall(r'/sf/detail/(\d{10}-P\d+P\d+)', h)))
print('detail URL数', len(urls))
base = sorted(set(u.split('-')[0] for u in urls))
print('base eid数', len(base))
txt = re.sub(r'\s+',' ', H.unescape(re.sub(r'<[^>]+>',' ', h)))
print(txt[:1500])
