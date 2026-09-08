# -*- coding: utf-8 -*-
"""1ページだけ落として、公演正式名がどのタグに入っているか探す。"""
import sys, re, io
sys.path.insert(0, 'tools')
from build_pia_entries import fetch

h = fetch('https://t.pia.jp/pia/event/event.do?eventCd=2635136')
open(r'C:\Users\user\oshinavi\tmp\probe_2635136.html', 'w', encoding='utf-8').write(h)
txt = re.sub(r'<script.*?</script>', '', h, flags=re.S)
txt = re.sub(r'<style.*?</style>', '', txt, flags=re.S)
txt = re.sub(r'<[^>]+>', '\n', txt)
lines = [re.sub(r'\s+', ' ', x).strip() for x in txt.split('\n')]
lines = [x for x in lines if x]
open(r'C:\Users\user\oshinavi\tmp\probe_2635136.txt', 'w', encoding='utf-8').write('\n'.join(lines[:200]))
print('OK len=%d lines=%d' % (len(h), len(lines)))
