# -*- coding: utf-8 -*-
# 宇崎竜童 43234 に抜けていた R9年 3/21 アクトシティ浜松（e+ 4472630001・10/24 から発売中）を組み立てて番人に通す（足すのは見てから）
import io, json, os, subprocess, sys
os.chdir('C:/Users/user/oshinavi')
env = dict(os.environ, PYTHONIOENCODING='utf-8')
D = 'tmp/x1124/art24/'
json.dump([{"eid": "4472630001", "title": "宇崎竜童 弾き語りLIVE2027 JUST GUITAR JUST VOCAL", "url": "https://eplus.jp/sf/detail/4472630001-P0030002P021001", "date": "2027-03-21"}],
          io.open(D + 'reg_hama_cands.json', 'w', encoding='utf-8'), ensure_ascii=False)
r = subprocess.run([sys.executable, 'tools/eplus_harvest.py', 'build', '99001', D + 'reg_hama_cands.json'], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
print(r.stdout[-1500:], r.stderr[-800:])
b = json.load(io.open('tmp/eplus_built.json', encoding='utf-8'))
json.dump(b, io.open(D + 'reg_hama_built.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(b, ensure_ascii=False, indent=1)[:2500])
g = subprocess.run([sys.executable, 'tools/gate_eplus_slots.py', D + 'reg_hama_built.json'], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
print('gate rc', g.returncode, g.stdout[-800:])
