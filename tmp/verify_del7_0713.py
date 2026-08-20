# -*- coding: utf-8 -*-
"""公演終了済み削除候補7件を、index.html の実URLでぴあ生HTML機械パースして裏取りする。
URLは手で書かず index.html から読む（feedback_no_fabricated_output）。"""
import re, json, sys, subprocess, time
sys.stdout.reconfigure(encoding='utf-8')

IDS = [771, 829, 1249, 1355, 1386, 2142, 2315]
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
E = {e['id']: e for e in json.loads(m.group(2))}

for i in IDS:
    e = E[i]
    url = (e.get('links') or {}).get('pia')
    print(f"\n=== id={i} {e.get('artist','')[:40]} @{e.get('venue','')[:24]} 公演{e.get('date','')}")
    r = subprocess.run([sys.executable, 'tools/pia_tickets.py', url, '--all'],
                       capture_output=True, text=True, encoding='utf-8')
    print(r.stdout.rstrip())
    if r.returncode != 0:
        print('  ❌ERROR', (r.stderr or '')[-200:])
    time.sleep(1.5)
