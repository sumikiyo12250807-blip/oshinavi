# -*- coding: utf-8 -*-
# 11/23 夜の鎖を作る（x1122 の形・すちこ「件数が減ってるわ　昨夜は夜通しを早く切り上げたみたいだけど、どうして？　新しい売り場からは収集しないの？」）
#  ①night_1123（夜の push）②night_collect23（ぴあ発売前の引き直し）③overnight_1123（e+ 出演者ページ＝🆕読み終えた印を消して二周目から）
#  ④night_newv23（新しい売り場5つの集め直し＝11/20 の形）⑤FANY の売り切れ全件（fany_mark_soldout --apply）＝すべて1本ずつ順に（メモリ）
import io, re
X = 'C:/Users/user/oshinavi/tmp/'
def cp(src, dst, pairs):
    s = io.open(X + src, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (src, a)
        s = s.replace(a, b)
    io.open(X + dst, 'w', encoding='utf-8').write(s)
    return s
# ① 夜の push
cp('x1122/night_1122.py', 'x1123/night_1123.py', [
    ("D = 'tmp/x1122/'", "D = 'tmp/x1123/'"), ("'night_1122.txt'", "'night_1123.txt'"),
    ("today_pia_ids.py', '2026-11-22'", "today_pia_ids.py', '2026-11-23'"),
    ("'night22_", "'night23p_"), ("'night_1122.done'", "'night_1123.done'"), ("'msg_night22.txt'", "'msg_night23p.txt'"),
    ("msg = ('11/22 夜の便（今日2回目）＝遅れた朝・昼の分（期限切れ 568件の削除・昼の隠れ枠ヒール 92件＋足し算 41件・e+ 今日発売・e+ 照合 3分の1・ぴあの見直し 今日の組・新着の振り分け）／X の独立FCで見つけた登録の崩れ（神田伯山・南佳孝）：今日発売のぴあ heal --ids・止まった分は足し算・HEAD比べ／prepush（畳み・会期・県・会場・欄・画面・並び・枠0・AI/artist ページ＝最終更新・compact）\\n\\n'",
     "msg = ('11/23 夜の便（今日2回目）＝抜き打ち30件の直し・TIGET 全件の作り直し・昼のヒール・ぴあの見直し 今日の組・夜の隠れ枠ヒール／🆕宿のボタンを売り場のバッジのすぐ下に横長で（押すと沈む）・最新CD を Amazon の商品ページへ 19枚・ボタンを数える仕掛けの直し：今日発売のぴあ heal --ids・止まった分は足し算・HEAD比べ／prepush（畳み・会期・県・会場・欄・画面・並び・枠0・AI/artist ページ＝最終更新・compact）\\n\\n'"),
])
# ② ぴあ発売前の引き直し
s = io.open(X + 'x1122/night_collect22.py', encoding='utf-8').read()
s2 = s.replace('tmp/x1122/', 'tmp/x1123/').replace('collect22', 'collect23').replace('2026-11-22', '2026-11-23').replace('11/22', '11/23')
io.open(X + 'x1123/night_collect23.py', 'w', encoding='utf-8').write(s2)
# ③ e+ 出演者ページ＝二周目（読み終えた印を消す・出演者の一覧は残す）
cp('x1122/overnight_1122.py', 'x1123/overnight_1123.py', [
    ("W = 'tmp/x1122/night_word10/'", "W = 'tmp/x1123/night_word11/'"),
    ("STOP = datetime.datetime(2026, 11, 23, 2, 0)", "STOP = datetime.datetime(2026, 11, 24, 2, 0)"),
    ("_p = json.load(io.open('tmp/x1121/night_word9/state.json', encoding='utf-8'))\n    json.dump({'done_urls': _p['done_urls'], 'wids': _p['wids'], 'cands': []}",
     "_p = json.load(io.open('tmp/x1122/night_word10/state.json', encoding='utf-8'))\n    # 🆕11/23 昨夜で一周読み終えた＝読み終えた印（done_urls）を消して二周目から（新しく出た公演を拾う）\n    json.dump({'done_urls': [], 'wids': _p['wids'], 'cands': []}"),
])
# ④ 新しい売り場5つ
s = io.open(X + 'x1120/night_newv20.py', encoding='utf-8').read()
s = s.replace('tmp/x1120/newv_n/', 'tmp/x1123/newv_n/').replace("io.open('tmp/x1120/assign_newv_n20.py', 'w'", "io.open('tmp/x1123/assign_newv_n23.py', 'w'").replace("run(['tmp/x1120/assign_newv_n20.py']", "run(['tmp/x1123/assign_newv_n23.py']")
s = s.replace("\"D = 'tmp/x1120/nassign_newv_n/'\"", "\"D = 'tmp/x1123/nassign_newv_n/'\"").replace('11/20 夜通し', '11/23 夜通し')
io.open(X + 'x1123/night_newv23.py', 'w', encoding='utf-8').write(s)
left = [l for l in s.splitlines() if 'x1120/newv_n' in l or 'assign_newv_n20.py' in l and 'open(' in l]
# 鎖
io.open(X + 'x1123/night_chain23.py', 'w', encoding='utf-8').write('''# -*- coding: utf-8 -*-
# 11/23 夜の鎖（1本ずつ）：night23（ぴあの見直し・夜のヒール）の .done を待つ → 夜の push → ぴあ発売前 → e+ 出演者ページ（二周目）→ 新しい売り場5つ → FANY 売り切れ全件
import io, os, subprocess, sys, time
os.chdir('C:/Users/user/oshinavi')
env = dict(os.environ, PYTHONIOENCODING='utf-8')
D = 'tmp/x1123/'
log = io.open(D + 'night_chain23.txt', 'a', encoding='utf-8')
def W(m):
    log.write(time.strftime('%H:%M:%S ') + m + '\\n'); log.flush()
while not os.path.exists(D + 'night23.done'):
    time.sleep(60)
for f in ('night_1123.py', 'night_collect23.py', 'overnight_1123.py', 'night_newv23.py'):
    W(f + ' 開始')
    r = subprocess.run([sys.executable, D + f], env=env)
    W(f + ' rc=%d' % r.returncode)
    open(D + f.replace('.py', '.done'), 'w').write(str(r.returncode))
W('fany_mark_soldout 開始')
r = subprocess.run([sys.executable, 'tools/fany_mark_soldout.py', '--apply'], env=env, capture_output=True, text=True, encoding='utf-8', errors='replace')
io.open(D + 'night_fany_soldout.txt', 'w', encoding='utf-8').write(r.stdout + r.stderr)
W('fany_mark_soldout rc=%d' % r.returncode)
r = subprocess.run([sys.executable, 'tmp/x1112/commit.py', D + 'msg_fany23.txt', 'tmp/fany_soldout_report.txt'], env=env)
open(D + 'night_chain23.done', 'w').write('done')
W('おわり')
''')
io.open(X + 'x1123/msg_fany23.txt', 'w', encoding='utf-8').write('11/23 夜通し（commit だけ）：FANY の売り切れ全件の点検（fany_mark_soldout --apply＝受付ページの「予定数終了」に印）\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01FQDm48dAXPgAGoNjRP5MVi\n')
io.open(X + 'x1123/mk_night23.txt', 'w', encoding='utf-8').write('ok 残った古い場所 %r\ncollect の変わった行 %d\n' % (left, sum(1 for a, b in zip(io.open(X + 'x1122/night_collect22.py', encoding='utf-8').read().splitlines(), s2.splitlines()) if a != b)))
