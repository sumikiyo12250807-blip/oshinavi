# -*- coding: utf-8 -*-
# 11/15 夜：新着プールの振り分け（すちこ「その後新着振り分けと収集お願いね」）＝assign_1115.py の夜版
#  対象＝新着のうち 売り場が1つ（ぴあ・e+・TIGET・FANY）・札が表にある・出演者が公演名でない分
#  （ZAIKO・livePocket は掲載許可の返事待ち＝触らない／売り場の分からない分も触らない）
#  番人を売り場ごとに1本ずつ順に（同時に叩かない）＝ぴあは今この場で reconcile_pia --ids → 出た id・gate_fields に出た id は残す → 振り分け → logs → commit
import io, json, os, re, sys, subprocess, time, collections
os.chdir('C:/Users/user/oshinavi')
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, 'tools')
import compact_events as C
import gate_fields as GF
env = dict(os.environ, PYTHONIOENCODING='utf-8')

_LK = 'tmp/x1112/index.lock'
while True:
    try:
        _fd = os.open(_LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(_fd, b'assign22n_other'); os.close(_fd); break
    except FileExistsError:
        time.sleep(15)
try:
    _t = io.open('index.html', encoding='utf-8', newline='').read()
    _gl = re.search(r'GENRE_LABEL\s*=\s*\{(.*?)\}', _t, re.S)
    _V = set(re.findall(r'["\']?([a-z0-9_.]+)["\']?\s*:', _gl.group(1))) - {'new'}
    _s, _e, _E = C.locate(_t)
    _n = []
    for _x in _E:
        if _x.get('genre') == 'new' and _x.get('_genre') not in _V:
            _x['_genre'] = 'other'
            _x['_otherByRule'] = '2026-11-21 すちこ「分からないものはその他に」＝あとで すちこが見て振り分け直す'
            _n.append(_x['id'])
    _t = _t[:_s] + C.dump(_E, True, '\r\n') + _t[_e:]
    io.open('index.html', 'w', encoding='utf-8', newline='').write(_t)
finally:
    os.remove(_LK)
D = 'tmp/x1122/nassign22n/'
os.makedirs(D, exist_ok=True)
log = io.open(D + 'log.txt', 'a', encoding='utf-8')
def L(m):
    log.write(time.strftime('%H:%M ') + m + '\n'); log.flush()
def run(a, out):
    r = subprocess.run([sys.executable] + a, capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    io.open(D + out, 'w', encoding='utf-8').write('rc=%d\n%s\n--stderr--\n%s' % (r.returncode, r.stdout, r.stderr[-4000:]))
    L('%s rc=%d' % (' '.join(a)[:80], r.returncode))
    return r.stdout
KEY = {'pia': 't.pia.jp', 'eplus': 'eplus.jp', 'tiget': 'tiget.net', 'fany': 'fany', 'ticketdive': 'ticketdive', 'ticketpay': 'ticketpay'}  # 🆕11/18 チケットペイも（すちこ「いいわ　チケットペイを振り分けて」）
OTHER = ('zaiko', 'livepocket', 'rakuten', 'l-tike', 'ticketdive', 'ticketpay', 'pia.jp', 'eplus.jp', 'tiget', 'fany')
text = io.open('index.html', encoding='utf-8', newline='').read()
gl = re.search(r'GENRE_LABEL\s*=\s*\{(.*?)\}', text, re.S)
VALID = set(re.findall(r'["\']?([a-z0-9_.]+)["\']?\s*:', gl.group(1))) - {'new'}
E = C.load(text)
L('はじめ カード=%d 新着=%d' % (len(E), sum(1 for e in E if e.get('genre') == 'new')))
L('札の無い新着を その他 に %d 件 %s' % (len(_n), _n))
io.open(D + 'other_ids.json', 'w').write(json.dumps(_n))
def urls(e):
    return (' '.join(t.get('url') or '' for t in e.get('tickets') or []) + ' ' +
            ' '.join(v or '' for k, v in (e.get('links') or {}).items() if k != 'amazon')).lower()
def vendors(e):
    u = urls(e)
    vs = set()
    for o in OTHER:
        if o in u:
            vs.add({'pia.jp': 'pia', 'eplus.jp': 'eplus', 'tiget': 'tiget'}.get(o, o))
    return vs
cand = collections.defaultdict(list)
for e in E:
    if e.get('genre') != 'new':
        continue
    vs = vendors(e)
    if len(vs) != 1:
        continue
    v = next(iter(vs))
    if v not in KEY:
        continue
    if e.get('_genre') not in VALID or GF.artist_looks_like_title(e):
        continue
    cand[v].append(e['id'])
L('候補 ' + str({k: len(v) for k, v in cand.items()}))
def ids_in(out, okmark=('✅',)):
    bad = set()
    for line in out.splitlines():
        if any(line.lstrip().startswith(m) for m in okmark):
            continue
        for grp in re.findall(r'id[=\s]?(\d{4,6}(?:,\d{4,6})*)', line):
            bad.update(int(x) for x in grp.split(','))
        # 🆕11/18 チケットペイの番人は「🚨 52489 event_id=65230」＝id の前に "id" が無い（event_id の売り場の番号を拾っていた）
        m = re.match(r'^(?:🚨\S*|❌)\s+(\d{4,6})\s+event_id=', line.strip())
        if m:
            bad.add(int(m.group(1)))
    return bad
def guard(v, rep_path, b):
    # 🆕11/18 番人が「合わない」と言った（🚨/❌ の行がある）のに id を1つも拾えなかったら、その売り場は振り分けない
    t = io.open(rep_path, encoding='utf-8').read()
    if not b and re.search(r'^(?:🚨|❌)', t, re.M):
        L('🚨 %s の番人の報告から id を読めなかった＝この売り場は振り分けない' % v)
        cand[v] = []
    return b
bad = collections.defaultdict(set)
if cand['ticketpay']:
    run(['tools/gate_ticketpay_slots.py', '--ids', ','.join(map(str, cand['ticketpay']))], 'tp.txt')
    bad['ticketpay'] = guard('ticketpay', 'tmp/gate_ticketpay_report.txt', ids_in(io.open('tmp/gate_ticketpay_report.txt', encoding='utf-8').read()))
if cand['tiget']:
    run(['tools/gate_tiget_slots.py', '--ids', ','.join(map(str, cand['tiget']))], 'tiget.txt')
    bad['tiget'] = guard('tiget', 'tmp/gate_tiget_report.txt', ids_in(io.open('tmp/gate_tiget_report.txt', encoding='utf-8').read()))
if cand['fany']:
    run(['tools/gate_fany_slots.py', '--ids', ','.join(map(str, cand['fany']))], 'fany.txt')
    bad['fany'] = guard('fany', 'tmp/gate_fany_report.txt', ids_in(io.open('tmp/gate_fany_report.txt', encoding='utf-8').read()))
if cand['ticketdive']:
    run(['tools/gate_ticketdive_slots.py', '--ids', ','.join(map(str, cand['ticketdive']))], 'td.txt')
    bad['ticketdive'] = guard('ticketdive', 'tmp/gate_ticketdive_report.txt', ids_in(io.open('tmp/gate_ticketdive_report.txt', encoding='utf-8').read()))
if cand['eplus']:
    o = run(['tools/reconcile_eplus.py', '--ids', ','.join(map(str, cand['eplus']))], 'eplus.txt')
    bad['eplus'] = ids_in(o)
io.open(D + 'eplus.done', 'w').write('done')   # ここから先は e+ を叩かない＝夜通しの収集（e+）を始めてよい
if 'nopia' in sys.argv:
    cand.pop('pia', None)
if cand.get('pia'):
    o = run(['tools/reconcile_pia.py', '--ids', ','.join(map(str, cand['pia']))], 'pia.txt')
    bad['pia'] = ids_in(o)
gf = run(['tools/gate_fields.py'], 'gate_fields.txt')
# 🆕11/20 午後 R（名前にフェスで fes の札なし）は止める型ではない＝振り分けで fes を足す（gate_fields の文言どおり）。
#   集計の行（=== …）と R の行の番号は拾わない（e+ 38・TIGET 8・FANY 1 がこれで止まっていた）
gfbad = {int(x) for l in gf.splitlines() if not l.startswith('===') and not re.match(r'\s*R\s', l)
         for x in re.findall(r'(?<!\d)(\d{4,6})(?!\d)', l)}
import unicodedata
go = set()
for v, ids in cand.items():
    ok = [i for i in ids if i not in bad[v] and i not in gfbad]
    L('%s 候補%d 番人に出た%d gate_fields に出た%d 振り分ける%d' % (v, len(ids), len(set(ids) & bad[v]), len(set(ids) & gfbad), len(ok)))
    go.update(ok)
json.dump(sorted(go), io.open(D + 'go.json', 'w'))
LK = 'tmp/x1112/index.lock'
while True:
    try:
        fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'assign22n'); os.close(fd); break
    except FileExistsError:
        time.sleep(15)
done = []
try:
    text = io.open('index.html', encoding='utf-8', newline='').read()
    E = C.load(text)
    for e in E:
        if e['id'] in go and e.get('genre') == 'new' and e.get('_genre') in VALID:
            e['genre'] = e['_genre']
            ex = [x for x in (e.get('_extraGenres') or []) if x != e['genre'] and x in VALID]
            if GF.FES_NAME.search(unicodedata.normalize('NFKC', e.get('name') or '')) and e['genre'] != 'fes' and 'fes' in VALID:
                ex.append('fes')   # feedback_fes_definition ①＝名前にフェス
            if ex:
                e['extraGenres'] = list(dict.fromkeys(list(e.get('extraGenres') or []) + ex))
            done.append(e)
    s, end, _ = C.locate(text)
    text = text[:s] + C.dump(E, True, '\r\n') + text[end:]
    dn = {e['id'] for e in done}
    mo = re.search(r'NEW_ORDER\s*=\s*\[([^\]]*)\]', text)
    kp = [x.strip() for x in mo.group(1).split(',') if x.strip() and int(x.strip()) not in dn]
    text = text[:mo.start(1)] + ','.join(kp) + text[mo.end(1):]
    io.open('index.html', 'w', encoding='utf-8', newline='').write(text)
finally:
    os.remove(LK)
def url(e):
    return next((t.get('url') for t in e.get('tickets') or [] if t.get('url')), '') or next(
        (x for k, x in (e.get('links') or {}).items() if x and k != 'amazon'), '')
lp = 'logs/assigned_2026-11-22.md'
Lg = ['', '## 11/22 夕方 新着の振り分け %d件（札の無い分は すちこ「分からないものはその他に」＝その他・売り場1つ・番人 gate_tiget_slots／gate_fany_slots／gate_ticketdive_slots／reconcile_eplus --ids／reconcile_pia --ids＋gate_fields に出なかった分・ジャンルは売り場の札）' % len(done)]
for e in sorted(done, key=lambda x: x['id']):
    Lg.append('- id=%s %s → %s%s ／ %s' % (e['id'], (e.get('name') or '')[:50], e['genre'],
              ('＋' + '・'.join(e['extraGenres'])) if e.get('extraGenres') else '', url(e)))
if not os.path.exists(lp):
    Lg.insert(0, '# 2026-11-22 振り分けたエントリ')
io.open(lp, 'a', encoding='utf-8').write('\n'.join(Lg) + '\n')
c = collections.Counter(e['genre'] for e in done)
L('振り分けた %d %s ／ 新着の残り %d' % (len(done), c.most_common(), len(kp)))
io.open(D + 'msg.txt', 'w', encoding='utf-8').write(
    '11/22 夕方（commit だけ）：新着の振り分け（すちこ「とりあえず分からないものはその他に入れておいて　わたしが後でチェックして振り分ける」＝札の無い分は その他）＝売り場1つ（ぴあ・e+・TIGET・FANY・TicketDive）・札あり・出演者ありの分を番人（gate_tiget_slots／gate_fany_slots／gate_ticketdive_slots／reconcile_eplus --ids／reconcile_pia --ids）＋gate_fields に通し、出なかった %d件を売り場の札で振り分け（logs/assigned_2026-11-22.md）\n\n'
    'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01FQDm48dAXPgAGoNjRP5MVi\n' % len(done))
if done:
    run(['tmp/x1112/commit.py', D + 'msg.txt', 'logs/assigned_2026-11-22.md', 'plan.md'], 'commit.txt')
io.open(D + 'done', 'w').write(str(len(done)))
L('おわり')
