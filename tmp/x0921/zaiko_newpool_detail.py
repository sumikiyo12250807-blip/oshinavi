# -*- coding: utf-8 -*-
"""ZAIKOの MUSCLE BEACH 4公演と Verrückt × unchained の個別ページを引いて、公演日・券種・状態を並べる（読むだけ）。
使い方: python tmp/x0921/zaiko_newpool_detail.py
出力: tmp/x0921/zaiko_newpool_detail.txt
"""
import importlib.util
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
spec = importlib.util.spec_from_file_location('zh', os.path.join(os.getcwd(), 'tools', 'zaiko_harvest.py'))
zh = importlib.util.module_from_spec(spec)
sys.argv = [sys.argv[0]]
spec.loader.exec_module(zh)

URLS = [
    'https://ageha.zaiko.io/ja/e/musclebeach26-osujiru',
    'https://ageha.zaiko.io/ja/e/musclebeach26-musclebeach',
    'https://ageha.zaiko.io/ja/e/musclebeach26-happyball',
    'https://ageha.zaiko.io/ja/e/musclebeach26-rokusyaku',
    'https://cultureofasia.zaiko.io/ja/e/verruckt-unchained',
]
o = io.open('tmp/x0921/zaiko_newpool_detail.txt', 'w', encoding='utf-8')
for u in URLS:
    d = zh.page_data(zh.fetch(u)) or {}
    ev = (d.get('props') or {}).get('event') or {}
    o.write('## %s\n  %s ｜%s ｜%s ｜status=%s\n' % (u, ev.get('name'), ev.get('display_date_period'),
                                                   ((ev.get('venue') or {}).get('data') or {}).get('name'), ev.get('status')))
    for t in ev.get('tickets') or []:
        o.write('   - %s %s sold_out=%s ended=%s started=%s\n' % (t.get('front_text') or t.get('name'), t.get('display_price'),
                                                                 t.get('is_sold_out'), t.get('is_sale_ended'), t.get('is_sale_started')))
    evs = (d.get('props') or {}).get('events')
    if evs:
        o.write('  props.events: %s\n' % json.dumps(evs, ensure_ascii=False)[:600])
o.close()
print('ok')
