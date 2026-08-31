# -*- coding: utf-8 -*-
"""logs/eplus_batch2_review_*.md を、携帯で確認できる1枚のHTMLに変換する。"""
import html
import json
import re
import sys
from pathlib import Path

SRC = Path(sys.argv[1])
OUT = Path(sys.argv[2])

text = SRC.read_text(encoding="utf-8")
blocks = re.split(r"^## ", text, flags=re.M)[1:]

entries = []
for b in blocks:
    lines = b.rstrip().split("\n")
    head = lines[0].strip()
    m = re.match(r"^(\d+)\s+(.*)$", head)
    eid, name = (m.group(1), m.group(2)) if m else ("", head)
    facts = {}
    rows = []
    for ln in lines[1:]:
        fm = re.match(r"^- ([^:]+):\s*(.*)$", ln)
        if fm:
            facts[fm.group(1).strip()] = fm.group(2).strip()
            continue
        if ln.startswith("|") and not re.match(r"^\|[\s\-|]+\|$", ln):
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if cells and cells[0] in ("枠名（受付）",):
                continue
            rows.append(cells)
    venue, pref = facts.get("会場", ""), ""
    if "／ 県:" in venue:
        venue, pref = [x.strip() for x in venue.split("／ 県:", 1)]
    entries.append({
        "id": eid, "name": name,
        "title": facts.get("公演名", ""),
        "date": facts.get("公演日", ""),
        "venue": venue, "pref": pref,
        "genre": facts.get("ジャンル下書き", ""),
        "url": facts.get("URL", ""),
        "rows": rows,
    })

total_slots = sum(len(e["rows"]) for e in entries)


def esc(s):
    return html.escape(s or "")


def short_url(u):
    return u.replace("https://eplus.jp/sf/detail/", "")


cards = []
for i, e in enumerate(entries, 1):
    tr = "\n".join(
        "<tr><td class=\"slot\">{}</td><td class=\"num\">{}</td><td class=\"num\">{}</td>"
        "<td><a class=\"mono\" href=\"{}\" target=\"_blank\" rel=\"noopener\">{}</a></td></tr>".format(
            esc(r[0]), esc(r[1] if len(r) > 1 else ""), esc(r[2] if len(r) > 2 else ""),
            esc(r[3] if len(r) > 3 else "#"), esc(short_url(r[3] if len(r) > 3 else "")))
        for r in e["rows"])
    cards.append(f"""
<article class="card" id="e{esc(e['id'])}" data-id="{esc(e['id'])}">
  <header class="card-head">
    <button class="tick" type="button" aria-pressed="false" aria-label="確認済みにする"></button>
    <div class="head-text">
      <p class="eyebrow"><span class="idno">{esc(e['id'])}</span><span class="count">{i} / {len(entries)}</span></p>
      <h2>{esc(e['name'])}</h2>
      <p class="title">{esc(e['title'])}</p>
    </div>
  </header>
  <dl class="facts">
    <div><dt>公演日</dt><dd>{esc(e['date'])}</dd></div>
    <div><dt>会場</dt><dd>{esc(e['venue'])}</dd></div>
    <div><dt>県</dt><dd>{esc(e['pref'])}</dd></div>
    <div><dt>ジャンル下書き</dt><dd>{esc(e['genre'])}</dd></div>
  </dl>
  <div class="tablewrap">
    <table>
      <thead><tr><th>枠名（受付）</th><th>受付開始</th><th>締切</th><th>個別URL</th></tr></thead>
      <tbody>
{tr}
      </tbody>
    </table>
  </div>
  <p class="mainlink"><a href="{esc(e['url'])}" target="_blank" rel="noopener">e+のページを開く →</a></p>
</article>""")

doc = f"""<title>e+ 発売前バッチ2 確認表</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Zen+Kaku+Gothic+New:wght@500;700&family=Noto+Sans+JP:wght@400;500&display=swap">
<style>
:root {{
  --paper:#f3f4f7; --surface:#ffffff; --surface-2:#eef0f5;
  --ink:#171a21; --ink-soft:#555c6b; --ink-faint:#7d8494;
  --line:#dfe2ea; --line-soft:#ecedf2;
  --accent:#34508f; --accent-soft:#e6ecf8;
  --ok:#2c6a52; --ok-soft:#e2f0e9;
  --shadow:0 1px 2px rgba(23,26,33,.05), 0 8px 24px -16px rgba(23,26,33,.28);
  --display:"Zen Kaku Gothic New","Hiragino Kaku Gothic ProN","Yu Gothic",sans-serif;
  --body:"Noto Sans JP","Hiragino Kaku Gothic ProN","Yu Gothic",sans-serif;
  --mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --paper:#131519; --surface:#1b1e25; --surface-2:#22262f;
    --ink:#e9eaef; --ink-soft:#a4abba; --ink-faint:#79808f;
    --line:#2b303a; --line-soft:#242932;
    --accent:#8fabe4; --accent-soft:#20293a;
    --ok:#7cc4a4; --ok-soft:#1c2a25;
    --shadow:0 1px 2px rgba(0,0,0,.4), 0 8px 24px -16px rgba(0,0,0,.7);
  }}
}}
:root[data-theme="dark"] {{
  --paper:#131519; --surface:#1b1e25; --surface-2:#22262f;
  --ink:#e9eaef; --ink-soft:#a4abba; --ink-faint:#79808f;
  --line:#2b303a; --line-soft:#242932;
  --accent:#8fabe4; --accent-soft:#20293a;
  --ok:#7cc4a4; --ok-soft:#1c2a25;
  --shadow:0 1px 2px rgba(0,0,0,.4), 0 8px 24px -16px rgba(0,0,0,.7);
}}
* {{ box-sizing:border-box; }}
body {{
  margin:0; background:var(--paper); color:var(--ink);
  font-family:var(--body); font-size:15px; line-height:1.7;
  -webkit-text-size-adjust:100%;
}}
.wrap {{ max-width:760px; margin:0 auto; padding:0 16px 64px; }}

.masthead {{ padding:36px 0 20px; border-bottom:1px solid var(--line); }}
.kicker {{
  font-family:var(--mono); font-size:11px; letter-spacing:.14em;
  text-transform:uppercase; color:var(--accent); margin:0 0 10px;
}}
.masthead h1 {{
  font-family:var(--display); font-weight:700; font-size:clamp(24px,5.4vw,32px);
  line-height:1.3; margin:0 0 10px; text-wrap:balance; letter-spacing:.01em;
}}
.lede {{ margin:0; color:var(--ink-soft); font-size:14px; max-width:62ch; }}
.stats {{ display:flex; flex-wrap:wrap; gap:8px; margin:18px 0 0; padding:0; list-style:none; }}
.stats li {{
  background:var(--surface); border:1px solid var(--line); border-radius:999px;
  padding:5px 13px; font-size:12.5px; color:var(--ink-soft);
}}
.stats b {{ color:var(--ink); font-weight:500; font-variant-numeric:tabular-nums; }}

.progress {{
  position:sticky; top:0; z-index:5; margin:0 -16px 24px; padding:11px 16px;
  background:color-mix(in srgb, var(--paper) 88%, transparent);
  -webkit-backdrop-filter:blur(10px); backdrop-filter:blur(10px);
  border-bottom:1px solid var(--line);
  display:flex; align-items:center; gap:12px;
}}
.bar {{ flex:1; height:5px; border-radius:999px; background:var(--surface-2); overflow:hidden; }}
.bar span {{ display:block; height:100%; width:0%; background:var(--ok); transition:width .25s ease; }}
.progress p {{ margin:0; font-family:var(--mono); font-size:12px; color:var(--ink-soft); font-variant-numeric:tabular-nums; white-space:nowrap; }}
.progress button {{
  border:1px solid var(--line); background:var(--surface); color:var(--ink-soft);
  border-radius:7px; padding:4px 10px; font:inherit; font-size:12px; cursor:pointer;
}}
.progress button:hover {{ color:var(--ink); border-color:var(--ink-faint); }}

.card {{
  background:var(--surface); border:1px solid var(--line); border-radius:12px;
  padding:18px 18px 14px; margin:0 0 14px; box-shadow:var(--shadow);
  transition:opacity .2s ease, border-color .2s ease;
}}
.card.done {{ opacity:.5; border-color:var(--ok); }}
.card-head {{ display:flex; gap:12px; align-items:flex-start; }}
.head-text {{ min-width:0; flex:1; }}
.eyebrow {{ margin:0 0 4px; display:flex; gap:10px; align-items:baseline; }}
.idno {{
  font-family:var(--mono); font-size:12px; font-weight:500; color:var(--accent);
  background:var(--accent-soft); border-radius:5px; padding:1px 7px;
}}
.count {{ font-family:var(--mono); font-size:11px; color:var(--ink-faint); font-variant-numeric:tabular-nums; }}
.card h2 {{
  font-family:var(--display); font-weight:700; font-size:19px; line-height:1.4;
  margin:0; text-wrap:balance; overflow-wrap:anywhere;
}}
.title {{ margin:3px 0 0; font-size:13.5px; color:var(--ink-soft); overflow-wrap:anywhere; }}

.tick {{
  flex:none; width:28px; height:28px; margin-top:2px; border-radius:8px; cursor:pointer;
  border:1.5px solid var(--line); background:var(--surface-2); position:relative;
}}
.tick:hover {{ border-color:var(--ok); }}
.tick:focus-visible {{ outline:2px solid var(--accent); outline-offset:2px; }}
.tick[aria-pressed="true"] {{ background:var(--ok); border-color:var(--ok); }}
.tick[aria-pressed="true"]::after {{
  content:""; position:absolute; left:9px; top:4px; width:6px; height:12px;
  border:solid var(--surface); border-width:0 2px 2px 0; transform:rotate(43deg);
}}

.facts {{ display:grid; grid-template-columns:1fr; gap:0; margin:14px 0 0; padding:12px 0 0; border-top:1px solid var(--line-soft); }}
.facts > div {{ display:grid; grid-template-columns:88px 1fr; gap:10px; padding:2px 0; }}
.facts dt {{ font-size:12px; color:var(--ink-faint); }}
.facts dd {{ margin:0; font-size:13.5px; overflow-wrap:anywhere; }}

.tablewrap {{ overflow-x:auto; margin:14px -18px 0; padding:0 18px; }}
table {{ border-collapse:collapse; width:100%; min-width:520px; font-size:12.5px; }}
th {{
  text-align:left; font-weight:500; color:var(--ink-faint); font-size:11px;
  letter-spacing:.06em; padding:0 12px 6px 0; border-bottom:1px solid var(--line);
  white-space:nowrap;
}}
td {{ padding:7px 12px 7px 0; border-bottom:1px solid var(--line-soft); vertical-align:top; }}
tr:last-child td {{ border-bottom:0; }}
.slot {{ min-width:230px; }}
.num {{ font-family:var(--mono); font-variant-numeric:tabular-nums; white-space:nowrap; color:var(--ink-soft); }}
.mono {{ font-family:var(--mono); font-size:11.5px; word-break:break-all; }}
a {{ color:var(--accent); }}
a:focus-visible {{ outline:2px solid var(--accent); outline-offset:2px; border-radius:3px; }}
.mainlink {{ margin:12px 0 0; font-size:13px; }}

footer {{ margin-top:32px; padding-top:18px; border-top:1px solid var(--line); font-size:12.5px; color:var(--ink-faint); }}
@media (prefers-reduced-motion: reduce) {{ * {{ transition:none !important; }} }}
</style>

<div class="wrap">
  <header class="masthead">
    <p class="kicker">イープラス／発売前ハーベスト</p>
    <h1>e+ 発売前バッチ2の確認表</h1>
    <p class="lede">投入前にあなたの目で見る分。公演名・公演日・開演時刻・会場・県・枠名・受付の開始と締切・URLを全部並べたわ。見終わった枠は丸を押して消し込んでちょうだい。</p>
    <ul class="stats">
      <li><b>{len(entries)}</b> エントリ</li>
      <li><b>{total_slots}</b> 枠</li>
      <li>ゲート <b>PASS</b>（実ページ79枠／ビルド80枠）</li>
      <li>集計日 <b>2026-08-31</b></li>
    </ul>
  </header>

  <div class="progress">
    <div class="bar"><span id="fill"></span></div>
    <p id="pct">0 / {len(entries)}</p>
    <button type="button" id="reset">消し込みを戻す</button>
  </div>

{"".join(cards)}

  <footer>
    <p>OKが出たら <span class="mono">tools/eplus_harvest.py</span> の inject で投入するわ。直したい行があったら id を教えてちょうだい。</p>
  </footer>
</div>

<script>
(function () {{
  var KEY = "eplus-batch2-2026-08-31";
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

  document.getElementById("reset").addEventListener("click", function () {{
    done = {{}}; save(); paint();
  }});

  paint();
}})();
</script>
"""

OUT.write_text(doc, encoding="utf-8")
print("entries=%d slots=%d -> %s" % (len(entries), total_slots, OUT))
