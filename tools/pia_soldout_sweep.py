# -*- coding: utf-8 -*-
"""ぴあの「売っている枠」を3日に1回見直す番人（2026-10-09 新設・ユーザー「発売から２日おきに見に行って確認すればいいかも」
🆕2026-10-10 ユーザー「３日に１回でいいよ」＝2日で一周だとぴあに当てる量が多い（429で開けなくなる）ので3組・3日で一周に変えた）。

  python tools/pia_soldout_sweep.py                 # 今日の組を照合して下見（書かない）→ logs/pia_sweep_YYYY-MM-DD.md
  python tools/pia_soldout_sweep.py --apply         # 売り切れの印を付ける
  python tools/pia_soldout_sweep.py --group 0|1|2   # 組を指定（既定＝今日の日付で自動・3日で一周）
  python tools/pia_soldout_sweep.py --ids 1,2       # id を指定

## なぜ要るか
ぴあだけ、登録済みの枠が売り切れたかを定期的に見ていなかった（TIGET・livePocket・ZAIKO・FANY・楽天は毎朝全件）。
2026-10-09 の抜き打ちで、ぴあが「予定枚数終了」なのに OSHINAVI は「買える」のまま（3324 立川立飛歌舞伎・
29835 AGESTOCK の木村柾哉／都の回）が見つかった＝誰かが見に行くまでずっと残る。

## やること
1. 振り分け済み・ぴあの枠が売っている（発売済み・印なし・締切が今日以降）エントリを id で3組に分け、今日の組だけ
2. `reconcile_pia.py --ids` で照合 → STALE（登録の枠がぴあの買える枠に無い）と MISSING（ぴあにあって登録に無い）を拾う
3. STALE の枠は、ぴあのページを全券種で読み（pia_tickets.py --all --json）、同じ県・同じ公演日の券種が
   「予定枚数終了・完売・売切」なら **soldout の印**を付ける（消さない＝[[feedback_soldout_keep_visible]]）。
   それ以外（受付終了・抽選受付終了・読めない）は触らずに報告
4. MISSING は id を報告に出す（取り直しは heal_stale_deadlines --ids → 足し算で当てる）
🚨ぴあは1本ずつ（429）。ほかのぴあの道具と同時に回さない。夜の便のあと（22:30〜）に回す。
"""
import datetime, io, json, os, re, subprocess, sys

ROOT = 'C:/Users/user/oshinavi/'
os.chdir(ROOT)
ENV = dict(os.environ, PYTHONIOENCODING='utf-8')
SOLD = re.compile(r'(予定枚数|完売|売り?切)')
PERF = re.compile(r'（([^（）]*?)\s*(R9年\s*)?(\d{1,2})/(\d{1,2})(?:〜(?:R9年\s*)?(\d{1,2})/(\d{1,2}))?[^（）]*公演）')


def load():
    text = io.open('index.html', encoding='utf-8', newline='').read()
    m = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
    st = m.start(1)
    E, end = json.JSONDecoder().raw_decode(text, st)
    return text, st, end, E


def save(text, st, end, E):
    compact = text[st:st + 3].startswith('[\r\n{') or text[st:st + 3].startswith('[\n{')
    body = ('[\n' + ',\n'.join(json.dumps(x, ensure_ascii=False, separators=(',', ':')) for x in E) + '\n]') if compact else json.dumps(E, ensure_ascii=False, indent=2)
    if '\r\n' in text[st:st + 3000]:
        body = body.replace('\r\n', '\n').replace('\n', '\r\n')
    io.open('index.html', 'wb').write((text[:st] + body + text[end:]).encode('utf-8'))


def live_pia(e, today):
    out = []
    for t in e.get('tickets') or []:
        u = t.get('url') or (e.get('links') or {}).get('pia') or ''
        if 'pia.jp' not in u or t.get('soldout') or (t.get('date') or '') < today:
            continue
        if t.get('startDate') and t['startDate'] > today:
            continue
        out.append(t)
    return out


def page_rows(url):
    r = subprocess.run([sys.executable, 'tools/pia_tickets.py', url, '--all', '--json'], capture_output=True, text=True,
                       encoding='utf-8', errors='replace', env=ENV)
    if r.returncode != 0 or not r.stdout.strip().startswith('['):
        return None
    return json.loads(r.stdout)


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    today = datetime.date.today().isoformat()
    apply = '--apply' in sys.argv
    text, st, end, E = load()
    by = {e['id']: e for e in E}
    if '--ids' in sys.argv:
        ids = [int(x) for x in sys.argv[sys.argv.index('--ids') + 1].split(',')]
        grp = 'ids'
    else:
        grp = int(sys.argv[sys.argv.index('--group') + 1]) if '--group' in sys.argv else datetime.date.today().toordinal() % 3
        ids = [e['id'] for e in E if e.get('genre') != 'new' and e['id'] % 3 == grp and live_pia(e, today)]
    rep = io.open(f'logs/pia_sweep_{today}.md', 'w', encoding='utf-8')
    rep.write(f'# ぴあの見直し {today}（組 {grp}・{len(ids)}件）\n\n')
    stale, missing, fetch_ng = [], [], []
    for k in range(0, len(ids), 150):
        chunk = ids[k:k + 150]
        r = subprocess.run([sys.executable, 'tools/reconcile_pia.py', '--ids', ','.join(map(str, chunk))], capture_output=True,
                           text=True, encoding='utf-8', errors='replace', env=ENV)
        cur = None
        for line in (r.stdout or '').splitlines():
            m = re.match(r'\S+ id=(\d+) ', line)
            if m:
                cur = int(m.group(1))
                continue
            if cur is None:
                continue
            m = re.search(r'STALE 登録「(.+?)」\((\d{4}-\d{2}-\d{2})\)', line)
            if m:
                stale.append((cur, m.group(1), m.group(2)))
            elif re.search(r'MISSING ぴあに', line):
                missing.append((cur, line.strip()))
            elif re.search(r'❌FETCH ぴあ', line):
                fetch_ng.append(cur)
        print(f'照合 {min(k + 150, len(ids))}/{len(ids)}  STALE {len(stale)} MISSING {len(missing)}', flush=True)
    marked, ended, unread = [], [], []
    cache = {}
    for i, pre, d in stale:
        e = by.get(i)
        if not e:
            continue
        cand = [t for t in e.get('tickets') or [] if (t.get('type') or '').startswith(pre) and (t.get('date') or '') == d and not t.get('soldout')]
        if not cand:
            continue
        t = cand[0]
        url = t.get('url') or (e.get('links') or {}).get('pia') or ''
        if url not in cache:
            cache[url] = page_rows(url)
        rows = cache[url]
        if rows is None:
            unread.append((i, t['type']))
            continue
        pm = PERF.search(t['type'])
        if not pm:
            unread.append((i, t['type']))
            continue
        prefs = [p for p in pm.group(1).split('・') if p]
        y = 2027 if pm.group(2) else 2026
        d0 = '%d-%02d-%02d' % (y, int(pm.group(3)), int(pm.group(4)))
        hit = [r for r in rows if (r.get('perfdate') or '') <= d0 <= (r.get('perf_end') or r.get('perfdate') or '')
               and (not prefs or any(p in (r.get('pref') or '') for p in prefs))]
        if hit and all(SOLD.search(r.get('statustext') or '') for r in hit if r.get('state') == '受付終了') \
                and any(SOLD.search(r.get('statustext') or '') for r in hit) and not any(r.get('state') in ('受付中', '発売前') for r in hit):
            marked.append((i, t['type']))
        else:
            ended.append((i, t['type'], '／'.join(sorted({r.get('statustext') or '' for r in hit})) or '同じ回の券種が見つからない'))
    if apply and marked:
        # 🚨照合に何時間もかかる＝そのあいだに他の道具が index.html を書く。最初に読んだ E を書き戻すと上書きになるので、
        #   書く直前に読み直して、印だけを当てる
        text, st, end, E = load()
        by2 = {e['id']: e for e in E}
        for i, ty in marked:
            for t in (by2.get(i) or {}).get('tickets') or []:
                if t.get('type') == ty and not t.get('soldout'):
                    t['soldout'] = True
                    t['soldoutSince'] = today
                    break
        save(text, st, end, E)
    rep.write(f'## 売り切れの印を付けた {len(marked)}枠{"" if apply else "（下見）"}\n')
    for i, ty in marked:
        rep.write(f'- id{i} {(by[i].get("name") or "")[:30]}｜{ty}\n')
    rep.write(f'\n## 買える枠に無いが売り切れではない（触らない） {len(ended)}枠\n')
    for i, ty, why in ended:
        rep.write(f'- id{i} {(by[i].get("name") or "")[:30]}｜{ty}｜ぴあ：{why}\n')
    rep.write(f'\n## ぴあにあって登録に無い（取り直し） {len(missing)}\n')
    for i, l in missing:
        rep.write(f'- id{i} {l}\n')
    rep.write(f'\n## 読めなかった {len(fetch_ng) + len(unread)}\n')
    for i in fetch_ng:
        rep.write(f'- id{i} 混雑ページ\n')
    for i, ty in unread:
        rep.write(f'- id{i} {ty}\n')
    print(f'=== 照合 {len(ids)}件 / 売り切れの印 {len(marked)} / 売り切れ以外 {len(ended)} / 取りこぼし {len(missing)} / 読めず {len(fetch_ng) + len(unread)} → logs/pia_sweep_{today}.md ===')
    io.open('tmp/pia_sweep_missing_ids.txt', 'w', encoding='utf-8').write(','.join(str(i) for i in sorted({i for i, _ in missing})))


if __name__ == '__main__':
    main()
