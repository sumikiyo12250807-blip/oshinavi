# -*- coding: utf-8 -*-
# 11/3 朝のルーチン（ぴあを叩かない分）：今日の発売時刻／期限切れ／バッジ0／楽天 再照合＋売り切れ下見／e+ heal_eplus_started 下見
import subprocess, sys, io, os, re, json, collections
os.chdir('C:/Users/user/oshinavi')
env = dict(os.environ, PYTHONIOENCODING='utf-8')
D = 'tmp/x1122/'
day = '2026-11-22'

s = io.open('index.html', encoding='utf-8').read()
i = s.index('const EVENTS = [') + len('const EVENTS = ')
E, _ = json.JSONDecoder().raw_decode(s[i:])
c = collections.Counter()
for e in E:
    for t in e.get('tickets') or []:
        if t.get('startDate') == day and not t.get('soldout'):
            m = re.search(r'(\d{1,2}:\d{2})発売', t.get('type') or '')
            c[m.group(1) if m else '?'] += 1
io.open(D + 'today_times.txt', 'w', encoding='utf-8').write(''.join(f'{k} {v}\n' for k, v in sorted(c.items())))

def run(args, out, node=False):
    cmd = (['node'] if node else [sys.executable]) + args
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    io.open(D + out, 'w', encoding='utf-8').write(f'rc={r.returncode}\n{r.stdout}\n{r.stderr[-3000:]}')
    return r.stdout

run(['tools/check_expired.py'], 'expired.txt')
run(['tools/check_zero_badge.js'], 'zero_badge.txt', node=True)
run(['tools/check_zero_badge.js', '--ids'], 'zero_badge_ids.txt', node=True)
st = run(['tools/rakuten_state.py'], 'rakuten_state.txt')
m = re.search(r'(?:--ids|id:)\s+([\d,]+)', st)
if m:
    run(['tools/reconcile_rakuten.py', '--ids', m.group(1)], 'rec_rakuten.txt')
run(['tools/rakuten_mark_soldout.py'], 'rakuten_soldout_dry.txt')
run(['tools/heal_eplus_started.py'], 'heal_eplus.txt')
run(['tools/check_unknown_end.py'], 'unknown_end.txt')
io.open(D + 'morning_local.done', 'w').write('done')
