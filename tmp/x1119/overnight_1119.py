# -*- coding: utf-8 -*-
# 11/12→11/13 夜通し：e+ の出演者ページ（/sf/word/<id>）の総ざらいで、ジャンル一覧に出ない未登録の公演を集める
#  ① 載っている e+ のカード（新着→登録済みの新しい順）の実ページから /sf/word/ の id を集め、出演者ページの公演のうち
#     まだ載っていない eid で、今日以降の受付がある公演だけを候補に（撮影会・特典会などは外す）… 03:30 まで
#  ② eplus_harvest build → gate_eplus_slots で名前の出た id を外す → もう一度 gate（json）で 合わない・取りこぼし・読めない を外す
#  ③ 鍵 → inject_built（新着）→ 鍵を返す → reconcile_eplus --ids（2枚目）→ gate_fields → HEAD比べ → commit（push しない）
#  止まっても続きから（段ごとの .done）
import io, json, os, re, shutil, subprocess, sys, time, datetime
os.chdir('C:/Users/user/oshinavi')
sys.path.insert(0, 'tools')
from eplus_harvest import fetch, parse_ld, parse_windows  # noqa: E402
import compact_events as C  # noqa: E402
env = dict(os.environ, PYTHONIOENCODING='utf-8')
D = 'tmp/x1112/'
W = 'tmp/x1119/night_word7/'
os.makedirs(W, exist_ok=True)
LK = D + 'index.lock'
# 11/13→11/14：昨夜の続き（読んだページ・出演者は飛ばす）。組み立てと番人に昨夜は6時間かかった＝朝までに終わるよう 02:00 で集めるのを止める
STOP = datetime.datetime(2026, 11, 20, 2, 0)
CAP = 100000
if not os.path.exists(W + 'state.json'):
    _p = json.load(io.open('tmp/x1118/night_word6/state.json', encoding='utf-8'))
    json.dump({'done_urls': _p['done_urls'], 'wids': _p['wids'], 'cands': []}, io.open(W + 'state.json', 'w', encoding='utf-8'), ensure_ascii=False)
TODAY = datetime.date.today()
NG = re.compile(r'撮影会|特典会|チェキ|握手|サイン会|ツーショット|メッセージタイム|展示|アートワーク展')
log = io.open(W + 'overnight.txt', 'a', encoding='utf-8')
def L(m):
    log.write(time.strftime('%H:%M ') + m + '\n'); log.flush()
def run(a, out, timeout=None):
    r = subprocess.run([sys.executable] + a, capture_output=True, text=True, encoding='utf-8', errors='replace', env=env, timeout=timeout)
    t = r.stdout + '\n--stderr--\n' + r.stderr[-6000:]
    io.open(W + out, 'w', encoding='utf-8').write('rc=%d\n%s' % (r.returncode, t))
    L('%s rc=%d %s' % (' '.join(a)[:70], r.returncode, ' | '.join(l for l in r.stdout.splitlines() if l.startswith('===') or '集計' in l or '候補' in l)[:400]))
    return r
def lock():
    while True:
        try:
            fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'overnight_word'); os.close(fd); return
        except FileExistsError:
            time.sleep(20)
def unlock():
    try:
        os.remove(LK)
    except FileNotFoundError:
        pass
def events():
    return C.load(io.open('index.html', encoding='utf-8', newline='').read())
def count():
    E = events()
    return len(E), sum(1 for e in E if e.get('genre') == 'new')

# ① 候補集め
if not os.path.exists(W + 'cands.done'):
    st_f = W + 'state.json'
    st = json.load(io.open(st_f, encoding='utf-8')) if os.path.exists(st_f) else {'done_urls': [], 'wids': [], 'cands': []}
    E = events()
    L('はじめ カード=%d 新着=%d' % (len(E), sum(1 for e in E if e.get('genre') == 'new')))
    raw = io.open('index.html', encoding='utf-8').read()
    have = set(re.findall(r'eplus\.jp/sf/detail/(\d{10})', raw))
    tg = sorted([e for e in E if (e.get('links') or {}).get('eplus')], key=lambda e: (e.get('genre') != 'new', -e['id']))
    urls = list(dict.fromkeys(e['links']['eplus'] for e in tg))
    done_u, wids, cands = set(st['done_urls']), list(st['wids']), st['cands']
    seen_w, seen_e = set(wids), {c['eid'] for c in cands}
    L('e+ のカード %d（ページ %d）・続きから %d' % (len(tg), len(urls), len(done_u)))
    n = 0
    for u in urls:
        if datetime.datetime.now() >= STOP:
            L('02:00 になったので集めるのを止める'); break
        if len(cands) >= CAP:
            L('候補 %d 件で止める（今夜はパソコンを消す＝夜の push までに終わらせる）' % len(cands)); break
        if u in done_u:
            continue
        done_u.add(u); n += 1
        try:
            h = fetch(u)
        except Exception:
            continue
        time.sleep(0.4)
        for wid in re.findall(r'/sf/word/(\d{10})', h):
            if wid in seen_w:
                continue
            seen_w.add(wid); wids.append(wid)
            try:
                wh = fetch('https://eplus.jp/sf/word/%s' % wid)
            except Exception:
                continue
            time.sleep(0.4)
            for du in sorted(set(re.findall(r'/sf/detail/(\d{10}-P\d+P\d+)', wh))):
                eid = du.split('-')[0]
                if eid in have or eid in seen_e:
                    continue
                seen_e.add(eid)
                try:
                    dh = fetch('https://eplus.jp/sf/detail/' + du)
                except Exception:
                    continue
                time.sleep(0.4)
                ld = parse_ld(dh)
                ws = [w for w in parse_windows(dh) if w['ed'] >= TODAY]
                if not ld or not ws:
                    continue
                title = ld[0].get('name') or ''
                if NG.search(title):
                    continue
                cands.append({'eid': eid, 'title': title, 'url': 'https://eplus.jp/sf/detail/' + du, 'date': ld[0].get('date'), '_word': wid})
        if n % 25 == 0:
            json.dump({'done_urls': sorted(done_u), 'wids': wids, 'cands': cands}, io.open(st_f, 'w', encoding='utf-8'), ensure_ascii=False)
            L('ページ %d / 出演者 %d / 候補 %d' % (len(done_u), len(wids), len(cands)))
    json.dump({'done_urls': sorted(done_u), 'wids': wids, 'cands': cands}, io.open(st_f, 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump(cands, io.open(W + 'cands.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    L('候補 %d（出演者 %d・ページ %d）' % (len(cands), len(wids), len(done_u)))
    io.open(W + 'cands.done', 'w').write(str(len(cands)))

# ② 組み立て → 番人2枚
if not os.path.exists(W + 'built.done'):
    E = events()
    nid = max(e['id'] for e in E) + 1
    r = run(['tools/eplus_harvest.py', 'build', str(nid), W + 'cands.json'], 'build.txt', timeout=4 * 3600)
    B = []
    if os.path.exists('tmp/eplus_built.json') and os.path.getmtime('tmp/eplus_built.json') > os.path.getmtime(W + 'cands.done'):
        shutil.copy('tmp/eplus_built.json', W + 'built.json')
        B = json.load(io.open(W + 'built.json', encoding='utf-8'))
    L('組み立て %d件' % len(B))
    go = []
    if B:
        g1 = run(['tools/gate_eplus_slots.py', W + 'built.json'], 'gate1.txt', timeout=4 * 3600)
        bad = {int(x) for x in re.findall(r'id(\d{5})', g1.stdout)}
        ok = [e for e in B if e['id'] not in bad]
        json.dump(ok, io.open(W + 'ok.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        run(['tools/gate_eplus_slots.py', W + 'ok.json', '--json', W + 'ok_gate.json'], 'gate2.txt', timeout=4 * 3600)
        g = json.load(io.open(W + 'ok_gate.json', encoding='utf-8')) if os.path.exists(W + 'ok_gate.json') else None
        if g is not None:
            drop = {int(b['id']) for b in g.get('bad') or []} | {int(m['id']) for m in g.get('missing_shows') or []}
            for u in g.get('unread') or []:
                if isinstance(u, dict) and u.get('id') is not None:
                    drop.add(int(u['id']))
            go = [e for e in ok if e['id'] not in drop]
            L('番人1で外す %d / 番人2で外す %d / 入れる %d' % (len(bad), len(drop), len(go)))
        else:
            L('番人2の結果が無い＝入れない')
    json.dump(go, io.open(W + 'go.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    io.open(W + 'built.done', 'w').write(str(len(go)))

# ③ 投入 → 照合 → commit
if not os.path.exists(W + 'inject.done'):
    G = json.load(io.open(W + 'go.json', encoding='utf-8'))
    ids = []
    if G:
        lock()
        try:
            nid = max(e['id'] for e in events()) + 1
            for k, e in enumerate(G):
                e['id'] = nid + k
            json.dump(G, io.open(W + 'inject.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            run(['tools/inject_built.py', W + 'inject.json'], 'inject.txt', timeout=3600)
        finally:
            unlock()
        ids = [e['id'] for e in G]
        run(['tools/reconcile_eplus.py', '--ids', ','.join(map(str, ids))], 'reconcile.txt', timeout=4 * 3600)
        # 🆕11/19 夜：e+ のジャンルの札を写す段（memory project_overnight_harvest で「11/18 に足した」とあったのに道具に入っていなかった＝11/19 は手で回した）
        run(['tools/eplus_genre.py', '--apply', '--lock', LK, '--ids', ','.join(map(str, ids))], 'genre.txt', timeout=3 * 3600)
        run(['tools/gate_fields.py'], 'gate_fields.txt')
        run(['tmp/heal_head_compare_1805.py'], 'hc.txt')
        io.open(W + 'msg.txt', 'w', encoding='utf-8').write(
            '11/19 夜通し（commit だけ）：e+ の出演者ページ（/sf/word/）の総ざらい（11/18 の続き）で未登録 %d件を組み立てて新着へ（番人2枚・reconcile_eplus --ids）\n\n'
            'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n'
            'Claude-Session: https://claude.ai/code/session_01FQDm48dAXPgAGoNjRP5MVi\n' % len(ids))
        run([D + 'commit.py', W + 'msg.txt'], 'commit.txt')
    json.dump(ids, io.open(W + 'new_ids.json', 'w'))
    io.open(W + 'inject.done', 'w').write(str(len(ids)))

# ④ TicketDive（11/15〜 毎日の列・鍵と commit は道具が自分で＝ここでは鍵を持たない）
if not os.path.exists(W + 'td.done'):
    import shutil as _sh
    _td = 'tmp/x1115/ticketdive/'
    for f in ('done', 'td_inject.txt'):
        if os.path.exists(_td + f):
            _sh.move(_td + f, _td + f + '.am')
    s2 = io.open('tmp/x1115/td_1115.py', encoding='utf-8').read().replace("'11/15（commit だけ）：TicketDive の新しい公演を集めて新着の先頭へ（11/12 から集めていなかった＝毎日の列に入れる）", "'11/19 夜通し（commit だけ）：TicketDive の新しい公演を集めて新着の先頭へ")
    io.open(W + 'td_night.py', 'w', encoding='utf-8').write(s2)
    run([W + 'td_night.py'], 'td.txt', timeout=3 * 3600)
    io.open(W + 'td.done', 'w').write('done')

L('おわり カード=%d 新着=%d' % count())
io.open(W + 'overnight.done', 'w').write('done')
