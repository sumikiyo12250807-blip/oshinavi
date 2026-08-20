# -*- coding: utf-8 -*-
"""新着44件(ぴあ分)を **別パーサ tools/pia_tickets.py** で取り直して独立突合する。

なぜ build_pia_entries で取り直さないか＝作った本人と同じコードなので必ず一致してしまう
（アンカリング＝[[feedback_verify_independent_not_anchored]]）。pia_tickets.py は
別実装の券種ダンパなので、**ビルダー側のバグが出れば食い違いとして見える**。

見るのは reconcile_pia が「未照合skip」と言って飛ばした所も含めた全枠:
 ①枠数（買える券種の数 vs 登録tickets）
 ②券種名（席種ラベルが落ちて別の券が1枠に潰れていないか）
 ③受付終了/予定枚数終了の混入
 ④県・公演日
"""
import json
import re
import subprocess
import sys
import time
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
news = sorted([e for e in EVENTS if e.get('genre') == 'new'], key=lambda x: x['id'])
pia = [e for e in news if (e.get('links') or {}).get('pia')]


def cds(e):
    s = json.dumps(e, ensure_ascii=False)
    out = []
    for c in re.findall(r'event(?:Bundle)?Cd=(\w+)', s):
        if c not in out:
            out.append(c)
    return out


def norm(s):
    return unicodedata.normalize('NFKC', s or '').replace(' ', '').replace('　', '')


def kenshu(title):
    """pia_tickets の title「券種 ／ 公演名」から券種名だけ取る（前後スペース付きの ／ が区切り）。"""
    parts = re.split(r'\s／\s', title or '')
    return parts[0].strip() if parts else (title or '')


lines = []
bad = 0
for n, e in enumerate(pia, 1):
    got = []
    err = None
    for cd in cds(e):
        try:
            r = subprocess.run([sys.executable, 'tools/pia_tickets.py', cd, '--json'],
                               capture_output=True, timeout=180)
            if r.returncode != 0:
                err = (r.stderr or b'').decode('utf-8', 'replace')[:120]
                continue
            got += json.loads(r.stdout.decode('utf-8'))
        except Exception as ex:
            err = str(ex)[:120]
        time.sleep(1.2)
    reg = e.get('tickets') or []
    problems = []
    if err and not got:
        problems.append(f'再取得できなかった: {err}')
    else:
        if len(got) != len(reg):
            problems.append(f'枠数 登録{len(reg)} ≠ 別パーサ{len(got)}')
        # 券種名（登録バッジの先頭＝券種名）が別パーサ側にあるか
        got_ks = [norm(kenshu(g['title'])) for g in got]
        for t in reg:
            head = norm(re.split(r'（', t.get('type') or '')[0])
            if head and not any(head in k or k in head for k in got_ks):
                problems.append(f'券種名が別パーサに無い: {(t.get("type") or "")[:52]}  / 実物={got_ks[:4]}')
        # 状態（受付終了の混入）
        for g in got:
            if g['state'] not in ('受付中', '発売前'):
                problems.append(f'買えない状態が混入: [{g["state"]}] {kenshu(g["title"])[:40]}')
    if problems:
        bad += 1
        lines.append(f"🚨 id={e['id']} {(e.get('artist') or '')[:40]}")
        for p in dict.fromkeys(problems):
            lines.append(f'    {p}')
    else:
        lines.append(f"✅ id={e['id']} {(e.get('artist') or '')[:40]} | 登録{len(reg)}=別パーサ{len(got)} 券種名一致")
    print(f'[{n}/{len(pia)}] {e["id"]} {"NG" if problems else "OK"}', flush=True)

lines.append('')
lines.append(f'=== ぴあ {len(pia)}件を別パーサで再取得 / 食い違い {bad}件 ===')
open('tmp/xcheck_new48_0730.txt', 'w', encoding='utf-8').write('\n'.join(lines))
print('wrote tmp/xcheck_new48_0730.txt  bad=%d' % bad)
