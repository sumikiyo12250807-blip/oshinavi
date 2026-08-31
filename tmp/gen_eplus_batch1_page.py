# -*- coding: utf-8 -*-
"""新着プールに入っている e+ エントリ（バッチ1）を、携帯で確認できる1枚のHTMLにする。
バッチ2の確認表と同じ作りだが、こちらは「もう画面に出ている」ので、
確認したいのは①中身が実ページと合っているか②どのジャンルに置くか の2点。"""
import glob
import html
import json
import re
import sys
from pathlib import Path

OUT = Path(sys.argv[1])

# e+ の一覧ジャンル → OSHINAVI のジャンル
GMAP = {'j-pop': ('jpop', 'J-POP'), 'rock-indies': ('rock', 'ロック'),
        'voiceactor-live': ('seiyuu', '声優'), 'visual': ('rock', 'ロック（ヴィジュアル系）')}

eid2g = {}
for p in glob.glob('tmp/*ep*083*.json') + ['tmp/eplus_live_cand.json']:
    try:
        d = json.load(open(p, encoding='utf-8'))
    except Exception:
        continue
    if isinstance(d, list):
        for c in d:
            if isinstance(c, dict) and c.get('eid') and c.get('_genre'):
                eid2g.setdefault(c['eid'], set()).add(c['_genre'])

src = open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'const EVENTS = (\[.*?\]);\n', src, re.S).group(1))
pool = [e for e in EVENTS if e.get('genre') == 'new' and (e.get('links') or {}).get('eplus')]


def srcgenre(e):
    urls = [(e.get('links') or {}).get('eplus', '')] + [t.get('url', '') for t in e.get('tickets', [])]
    gs = set()
    for u in urls:
        m = re.search(r'/sf/detail/(\d+)', u or '')
        if m:
            gs |= eid2g.get(m.group(1), set())
    return sorted(gs)


def esc(s):
    return html.escape(s or '')


CSS = open('tmp/_eplus_page.css', encoding='utf-8').read()

cards = []
counts = {}
for i, e in enumerate(sorted(pool, key=lambda x: x['id']), 1):
    gs = srcgenre(e)
    tgt = GMAP.get(gs[0], ('musicetc', 'その他')) if gs else ('musicetc', 'その他')
    counts[tgt[1]] = counts.get(tgt[1], 0) + 1
    rows = '\n'.join(
        '<tr><td class="slot">{}</td><td class="num">{}</td><td class="num">{}</td>'
        '<td><a class="mono" href="{}" target="_blank" rel="noopener">{}</a></td></tr>'.format(
            esc(t.get('type')), esc(t.get('startDate') or '—'), esc(t.get('date')),
            esc(t.get('url') or (e.get('links') or {}).get('eplus') or '#'),
            esc((t.get('url') or '').replace('https://eplus.jp/sf/detail/', '') or '—'))
        for t in e.get('tickets', []))
    cards.append(f"""
<article class="card" id="e{e['id']}" data-id="{e['id']}">
  <header class="card-head">
    <button class="tick" type="button" aria-pressed="false" aria-label="確認済みにする"></button>
    <div class="head-text">
      <p class="eyebrow"><span class="idno">{e['id']}</span><span class="count">{i} / {len(pool)}</span>
        <span class="genre">{esc(tgt[1])}</span></p>
      <h2>{esc(e.get('artist'))}</h2>
      <p class="title">{esc(e.get('name'))}</p>
    </div>
  </header>
  <dl class="facts">
    <div><dt>公演日</dt><dd>{esc(e.get('dateLabel'))}</dd></div>
    <div><dt>会場</dt><dd>{esc(e.get('venue'))}</dd></div>
    <div><dt>県</dt><dd>{esc(e.get('prefecture'))}</dd></div>
    <div><dt>千秋楽</dt><dd>{esc(e.get('date'))}</dd></div>
    <div><dt>e+の区分</dt><dd>{esc('／'.join(gs) or '不明')}</dd></div>
  </dl>
  <div class="tablewrap">
    <table>
      <thead><tr><th>枠名（受付）</th><th>受付開始</th><th>締切</th><th>個別URL</th></tr></thead>
      <tbody>
{rows}
      </tbody>
    </table>
  </div>
  <p class="mainlink"><a href="{esc((e.get('links') or {}).get('eplus'))}" target="_blank" rel="noopener">e+のページを開く →</a></p>
</article>""")

stat = '／'.join(f'{k} {v}件' for k, v in sorted(counts.items(), key=lambda x: -x[1]))
doc = f"""<title>e+ 新着バッチ1 確認表</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Zen+Kaku+Gothic+New:wght@500;700&family=Noto+Sans+JP:wght@400;500&display=swap">
<style>
{CSS}
.genre {{ font-size:11px; color:var(--ok); background:var(--ok-soft); border-radius:5px; padding:1px 8px; }}
</style>

<div class="wrap">
  <header class="masthead">
    <p class="kicker">イープラス／新着プールに掲載中</p>
    <h1>e+ 新着バッチ1の確認表</h1>
    <p class="lede">こちらは<b>もう画面の「✨新着」タブに出ている</b>分よ。今朝、会場と公演期間が実ページより狭かった8件を作り直したから、その結果も入ってるわ。見てほしいのは中身が合っているかと、右上のジャンルでいいかの2つ。</p>
    <ul class="stats">
      <li><b>{len(pool)}</b> エントリ</li>
      <li><b>{sum(len(e.get('tickets', [])) for e in pool)}</b> 枠</li>
      <li>ジャンル案 {esc(stat)}</li>
    </ul>
    <p class="note">ジャンルは e+ の一覧区分をそのまま写す方針で当てたわ（j-pop→J-POP／rock-indies→ロック／voiceactor-live→声優）。
    <b>ヴィジュアル系(visual)だけ行き先が無い</b>ので、いまはロックに寄せてある。専用タブを作るなら言ってちょうだい。</p>
  </header>

  <div class="progress">
    <div class="bar"><span id="fill"></span></div>
    <p id="pct">0 / {len(pool)}</p>
    <button type="button" id="reset">消し込みを戻す</button>
  </div>

{"".join(cards)}

  <footer>
    <p>OKが出たら <span class="mono">tools/assign_genres.py</span> でジャンルに振り分けるわ。直したい行があったら id を教えてちょうだい。</p>
  </footer>
</div>

<script>
(function () {{
  var KEY = "eplus-batch1-2026-09-01";
  var cards = Array.prototype.slice.call(document.querySelectorAll(".card"));
  var fill = document.getElementById("fill");
  var pct = document.getElementById("pct");
  var done = {{}};
  try {{ done = JSON.parse(localStorage.getItem(KEY) || "{{}}") || {{}}; }} catch (e) {{ done = {{}}; }}
  function save() {{ try {{ localStorage.setItem(KEY, JSON.stringify(done)); }} catch (e) {{}} }}
  function paint() {{
    var n = 0;
    cards.forEach(function (c) {{
      var on = !!done[c.dataset.id];
      if (on) n++;
      c.classList.toggle("done", on);
      c.querySelector(".tick").setAttribute("aria-pressed", on ? "true" : "false");
    }});
    fill.style.width = (cards.length ? (n / cards.length) * 100 : 0) + "%";
    pct.textContent = n + " / " + cards.length;
  }}
  cards.forEach(function (c) {{
    c.querySelector(".tick").addEventListener("click", function () {{
      var id = c.dataset.id;
      if (done[id]) {{ delete done[id]; }} else {{ done[id] = 1; }}
      save(); paint();
    }});
  }});
  document.getElementById("reset").addEventListener("click", function () {{ done = {{}}; save(); paint(); }});
  paint();
}})();
</script>
"""
OUT.write_text(doc, encoding='utf-8')
print('entries=%d -> %s / %s' % (len(pool), OUT, stat))
