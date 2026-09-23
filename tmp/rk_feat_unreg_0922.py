# -*- coding: utf-8 -*-
"""楽天特設ページから辿れる公演ページ（events）のうち、index.html に無い rtXXXX を数える。
公演日が今日以降の行を持つものだけ。"""
import io, json, re, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
src = io.open('index.html', encoding='utf-8').read()
d = json.load(io.open('tmp/rakuten_features.json', encoding='utf-8'))
ev = d['events']
print('events型', type(ev).__name__, len(ev))
sample = ev[0] if isinstance(ev, list) else next(iter(ev.items()))
print('例', json.dumps(sample, ensure_ascii=False)[:600])
