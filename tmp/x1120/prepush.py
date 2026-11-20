# -*- coding: utf-8 -*-
# 11/1 push 前：畳み → 欄 → 画面 → 並び → 枠0 → (reconcile_pia --new) → AIページ・アーティストページ → compact → tmp/x1119/prepush.txt
# --no-rec ＝ぴあを別の係が組み立て中（2本同時に叩かない）・朝の照合は morning_pia が回し済み（そのあとぴあの新着は入れていない）
# index.html を書く間は鍵を持つ
import subprocess, sys, os, io, time, datetime
os.chdir('C:/Users/user/oshinavi')
sys.stdout.reconfigure(encoding='utf-8')
env = dict(os.environ, PYTHONIOENCODING='utf-8')
D = 'tmp/x1120/'
out = io.open(D + 'prepush.txt', 'w', encoding='utf-8')
def run(args, n=6, node=False):
    r = subprocess.run((['node'] if node else [sys.executable]) + args, capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    t = (r.stdout + r.stderr).strip().splitlines()
    out.write(f'=== {" ".join(args)[:70]} rc {r.returncode}\n' + '\n'.join(t[-n:]) + '\n'); out.flush()
    return r.returncode
d0 = datetime.date.today()
days = f'{d0.isoformat()},{(d0 + datetime.timedelta(days=1)).isoformat()}'
LK = 'tmp/x1112/index.lock'
while True:
    try:
        fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'prepush'); os.close(fd); break
    except FileExistsError:
        time.sleep(15)
try:
    run(['tools/fold_parts.py', '--apply'], 3)
    run(['tools/fill_span_from_slots.py', '--apply'], 2)
    run(['tools/fill_slot_pref.py', '--apply'], 2)
    run(['tools/fill_entry_pref.py', '--apply'], 2)
    run(['tools/fill_venue_from_slots.py', '--apply'], 2)  # 11/17〜 鍵は prepush が持っている＝--lock を付けない（入れ子にしない）
    run(['tools/fix_stale_rep_link.py', '--apply'], 2)  # 11/20〜 大きいリンクが締切の過ぎた枠だけを指す（抜き打ち 44612）
    run(['tools/fix_stale_rep_link.py'], 2)            # 残れば止める
    run(['tools/fold_parts.py', '--check'], 3)
    run(['tools/gate_fields.py'], 2)
    run(['tools/gate_badge_render.py', '--today', days], 4)
    run(['tools/check_order.js'], 4, node=True)
    run(['tools/check_zero_badge.js'], 3, node=True)
    if '--no-rec' not in sys.argv:
        run(['tools/reconcile_pia.py', '--new'], 8)
    run(['tools/build_ai_page.py'], 3)
    run(['tools/gate_artist_pages.py'], 4)
    run(['tools/compact_events.py', '--apply'], 3)
finally:
    os.remove(LK)
io.open(D + 'prepush.done', 'w').write('done')
print(io.open(D + 'prepush.txt', encoding='utf-8').read())
