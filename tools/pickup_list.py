# -*- coding: utf-8 -*-
"""記事を「1本ずつ足して、受付が終わったら下ろす」形で並べる（2026-11-09 新設）。

すちこ 11/8夜「記事を一日３本づつくらいたしていくの」「終わったらさげてよ」「記事の順番は発売日順にして」
＝週1の号の差し替えは失効。記事1本＝1ページ（pickup/a/<slug>.html・11/8号の組のページもそのまま1本として数える）。

台帳＝tools/pickup_articles.json（記事ごとに 載せた日・見るエントリid・数える受付の発売日の下限）
やること：
  1. 記事ごとに、見る id の枠のうち「まだ買える受付」を数える（売り切れの印・締切が過ぎた枠は数えない。
     締切が出ていない枠＝発売日と締切が同じ日の枠は、画面と同じく発売日の翌日まで）
  2. 買える受付が0になった記事は一覧から下ろす（ページのファイルは消さない＝Xから来た人が404にならない）
  3. index.html の記事欄＝新しい記事3本＋「記事の一覧」ボタン／pickup/index.html＝載っている記事の全部
     並び＝載せた日の新しい順・同じ日の中は発売日時の早い順（台帳の並び）

使い方: python tools/pickup_list.py            # 下見（書かない）
        python tools/pickup_list.py --apply    # index.html の記事欄と pickup/index.html を書き直す
"""
import datetime, html as H, io, json, os, re, subprocess, sys, time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
REG = 'tools/pickup_articles.json'
TOP_N = 3


def load_events():
    s = io.open('index.html', encoding='utf-8').read()
    i = s.index('const EVENTS = [') + len('const EVENTS = ')
    return json.JSONDecoder().raw_decode(s[i:])[0]


def alive_until(t, today, frm):
    """その枠が今日まだ買えるなら、いつまで（YYYY-MM-DD）。買えないなら None"""
    if t.get('soldout'):
        return None
    sd, d = t.get('startDate') or '', t.get('date') or ''
    if frm and sd < frm:
        return None
    if not d:
        return None
    if sd and sd == d and '〜' not in (t.get('type') or ''):
        last = (datetime.date.fromisoformat(sd) + datetime.timedelta(days=1)).isoformat()
        return last if today <= last else None
    return d if d >= today else None


def status(arts, E, today):
    by = {e.get('id'): e for e in E}
    out = []
    for a in arts:
        best, n, missing = None, 0, []
        for w in a['watch']:
            e = by.get(w)
            if not e:
                missing.append(w)
                continue
            for t in e.get('tickets') or []:
                u = alive_until(t, today, a.get('from'))
                if u:
                    n += 1
                    best = max(best or u, u)
        out.append(dict(a, live=n, until=best, missing=missing))
    return out


def item(a, href):
    ls = ''.join(f'\n    <span class="pk-i-line">{x}</span>' for x in a['lines'])
    return (f'  <a class="pk-item" href="{href}" target="_blank" rel="noopener">\n'
            f'    <span class="pk-i-name">{H.escape(a["name"])}</span>{ls}\n  </a>')


ITEM_CSS = """    .pickup a.pk-item { display: block; padding: 14px 2px; border-bottom: 1px solid var(--border); text-decoration: none; color: var(--text); transition: .2s; }
    .pickup .pk-sub + a.pk-item { border-top: 1px solid var(--border); }
    .pickup a.pk-item:hover, .pickup a.pk-item:focus-visible { background: rgba(224,64,251,.08); }
    .pickup .pk-i-name { display: block; font-size: 17px; font-weight: 900; color: var(--accent); text-decoration: underline; text-underline-offset: 4px; margin-bottom: 4px; }
    .pickup .pk-i-line { display: block; font-size: 14.5px; line-height: 1.75; text-decoration: underline; text-decoration-color: rgba(255,255,255,.25); text-underline-offset: 4px; }
    .pickup .pk-i-line b { color: var(--accent2); font-weight: 800; font-size: 13px; }"""


def top_section(live):
    items = '\n'.join(item(a, a['href']) for a in live[:TOP_N])
    return f"""<section class="pickup" id="pickup">
  <style>
    /* 11/9〜 記事は1本ずつ足して、受付が終わったら下ろす（tools/pickup_list.py が書く） */
    .pickup a.pk-more {{ text-align: center; text-decoration: none; margin-top: 14px; }}
    .pickup a.pk-more::after {{ content: ' →'; }}
{ITEM_CSS}
  </style>
  <span class="pk-label">📖 ピックアップ記事</span>
  <p class="pk-sub">チケットが買えるうちだけ載せている記事よ（新しい順）</p>
{items}
  <a class="pk-more" href="pickup/index.html" target="_blank" rel="noopener">記事の一覧（{len(live)}本）</a>
</section>"""


def list_page(live):
    tpl = io.open('pickup/2026-11-08/index.html', encoding='utf-8').read()
    head = tpl[:tpl.index('<body>')]
    desc = 'チケットが買えるうちだけ載せている OSHINAVI の記事の一覧（新しい順）'
    head = re.sub(r'<title>.*?</title>', '<title>ピックアップ記事の一覧 - OSHINAVI</title>', head)
    head = re.sub(r'(<meta name="description" content=")[^"]*', r'\g<1>' + desc, head)
    head = re.sub(r'(<meta property="og:description" content=")[^"]*', r'\g<1>' + desc, head)
    head = re.sub(r'(<meta property="og:title" content=")[^"]*', r'\g<1>ピックアップ記事の一覧', head)
    head = head.replace('https://oshinavi.jp/pickup/2026-11-08/', 'https://oshinavi.jp/pickup/')
    head = head.replace('.pickup .pk-h2 + a.pk-item', '.pickup .pk-sub + a.pk-item')
    items = '\n'.join(item(a, '../' + a['href'][len('pickup/'):] if a['href'].startswith('pickup/') else a['href'])
                      for a in live)
    items = items.replace(' target="_blank" rel="noopener"', '')
    return head + f"""<body>

<header>
  <a href="../index.html" class="logo">OSHINAVI</a>
  <a href="../index.html" class="nav-back">← チケット・イベント一覧へ</a>
</header>

<main class="wrap">
<article class="pickup" id="pickup">
  <span class="pk-label">📖 ピックアップ記事</span>
  <h1 class="pk-title">ピックアップ記事の一覧</h1>
  <p class="pk-sub">チケットが買えるうちだけ載せている記事よ（新しい順）</p>
{items}
  <a class="pk-tail" href="../index.html?status=urgent">他にも気になるアーティストがチケット発売しているわよ。<span class="pk-go">今週発売を見る →</span></a>
</article>
</main>

</body>
</html>
"""


def main():
    apply = '--apply' in sys.argv
    today = datetime.date.today().isoformat()
    R = json.load(io.open(REG, encoding='utf-8'))
    arts = R['articles']
    st = status(arts, load_events(), today)
    # 載せた日の新しい順（同じ日の中は台帳の並び＝発売日時の早い順）
    order = sorted(range(len(st)), key=lambda k: (st[k]['added'], -k), reverse=True)
    live = [st[k] for k in order if st[k]['live']]
    down = [st[k] for k in order if not st[k]['live']]
    for a in live:
        print(f"載せる {a['added']} {a['name']}｜買える受付 {a['live']}・いちばん遅い締切 {a['until']}"
              + (f"｜⚠ 台帳の id が無い {a['missing']}" if a['missing'] else ''))
    for a in down:
        print(f"下ろす {a['added']} {a['name']}｜買える受付 0" + (f"｜⚠ 台帳の id が無い {a['missing']}" if a['missing'] else ''))
    print(f'載せる {len(live)} / 下ろす {len(down)}')
    if not apply:
        return
    for k, a in enumerate(st):
        if not a['live'] and not arts[k].get('down'):
            arts[k]['down'] = today
    io.open(REG, 'w', encoding='utf-8').write(json.dumps(R, ensure_ascii=False, indent=1))
    io.open('pickup/index.html', 'w', encoding='utf-8').write(list_page(live))
    os.makedirs('tmp/pickup_list', exist_ok=True)
    io.open('tmp/pickup_list/section.html', 'w', encoding='utf-8').write(top_section(live))
    r = subprocess.run([sys.executable, 'tools/apply_pickup.py', 'tmp/pickup_list/section.html'],
                       capture_output=True, text=True, encoding='utf-8', errors='replace',
                       env=dict(os.environ, PYTHONIOENCODING='utf-8'))
    print('apply_pickup rc', r.returncode, r.stdout[-800:], r.stderr[-500:])
    # ヘッダーの「今週のピックアップ」は記事の一覧へ（文字はそのまま）
    b = io.open('index.html', 'rb').read()
    b2 = re.sub(rb'<a href="pickup/[0-9-]+/index\.html" target="_blank" rel="noopener">',
                b'<a href="pickup/index.html" target="_blank" rel="noopener">', b)
    if b2 != b:
        io.open('index.html', 'wb').write(b2)
    print('ヘッダーのリンク', b2.count(b'<a href="pickup/index.html" target="_blank" rel="noopener">'), '本',
          '改行二重化', b'\r\r\n' in b2)
    sys.exit(r.returncode)


if __name__ == '__main__':
    main()
