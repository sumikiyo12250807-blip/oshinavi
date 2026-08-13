# -*- coding: utf-8 -*-
"""保存memoryの棚卸し用の一覧表(HTML)を作る。

  python tools/memory_audit.py

「どれが本当に要るか」をユーザーが自分で判断できるように、1件1行で
  種類 / 最終更新 / 文字数 / 被リンク数 / PLAYBOOK掲載 / MEMORY.md掲載 / 説明
を出す。捨てる候補の目安＝**被リンク0 かつ PLAYBOOK未掲載 かつ 古い**。
出力: memory_audit.html（memoryフォルダ内・ブラウザで開く）
"""
import datetime
import html
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MEM = r"C:\Users\user\.claude\projects\C--Users-user-oshinavi\memory"
PLAYBOOK = r"C:\Users\user\oshinavi\PLAYBOOK.md"
OUT = os.path.join(MEM, "memory_audit.html")

# ── 処理済みの記録（消えたファイルは表から居なくなるので、ここに履歴として残す）──
# 第1弾 2026-08-10：MEMORY.md索引にもPLAYBOOKにも載っていなかった13件を全文読んで判定した分。
DONE = [
    ("2026-08-10", "drop", "project_url_cleanup_progress",
     "4/21の作業ログ。「index.html 919件」の時代で、次の5件リストも全部処理済み。教訓は他memoryに現存"),
    ("2026-08-10", "drop", "project_hajimerin_pending",
     "本文に【完了】と明記。一凛はid2764に統合済みで宿題ゼロ"),
    ("2026-08-10", "drop", "feedback_careful_one_by_one",
     "「1件ずつ丁寧に」が feedback_pace_and_quality のペースダウン禁止と正面衝突＝古いだけでなく害があった"),
    ("2026-08-10", "drop", "feedback_kanto_50",
     "events.html専用の件数目標（1都県50件）。ページごと6/25に廃止＝救う1行なし"),
    ("2026-08-10", "drop", "feedback_events_no_autohide",
     "events.html専用の表示仕様。index.htmlは逆ルール（期限切れは載せない）で、残すと混乱の元"),
    ("2026-08-10", "drop", "feedback_events_link",
     "events.html専用。「個別の公式ページを貼る」は link_quality／require_specific_url／official_first に同内容が現存"),
    ("2026-08-10", "drop", "feedback_fireworks",
     "「有料花火はindex＋eventsの両方に載せる」の行楽側が消滅。残りはハーベストで自動的にそうなる（ユーザー判断で削除）"),
    ("2026-08-10", "merge", "feedback_event_size",
     "→ feedback_oshikatsu_first ｜移した1行＝<b>index.htmlはライブハウス小箱200〜300人も載せる</b>（発売前スイープで弾かない）"),
    ("2026-08-10", "merge", "project_url_recheck_id85",
     "→ reference_ltike_machine_unreachable ｜移した1行＝ローチケは発売直前まで個別公演ページが立たない＝推測で埋めず発売2〜3日前に取り直す"),
    ("2026-08-10", "merge", "feedback_ketsumeishi_lawson",
     "→ feedback_vendor_priority ｜移した1行＝そこで売っていないのに楽天リンクを貼らない（ケツメイシ＝ローチケ主力）"),
    ("2026-08-10", "merge", "feedback_new_genre_workflow",
     "→ feedback_new_pool_ok_before_assign ｜移した1行＝新着プールの定義（genre:new／verified:true／✨新着タブ）。"
     "旧「チェック済みは即振り分け」は7/31の教訓で無効と明記して復活を封じた"),
    ("2026-08-10", "keep", "project_events_html_abolished",
     "events.htmlを勝手に復活させないための唯一の記録。索引に無く死蔵だったので MEMORY.md に追加した"),
    ("2026-08-10", "keep", "project_time_aware_sale_status",
     "「アクセスが増えたら発売時刻判定を実装」の予約が生きている。同じく MEMORY.md に追加した"),
    # 第2弾 2026-08-10：表の上から順にユーザーと相談しながら。
    ("2026-08-10", "drop", "feedback_pre_add_cross_check",
     "「2サイト以上でクロスチェック」を言うだけの薄い重複。手順は feedback_cross_verification 側にあった＝消しても失う情報ゼロ"),
    ("2026-08-10", "merge", "feedback_cross_verification",
     "→ feedback_harvest_source_order_and_far_deadline ｜移した1行＝<b>機械ゲートは「登録⇄その売り場の実態」しか見ない＝売り場自体の誤りは範囲外</b>。"
     "だから①e+単独で公式の裏も取れないものは勝手に登録しない ②楽天に無い＝不一致ではない（大型フェスでも個別ページを持たない）。"
     "手作業の2サイト照合そのものは機械二段構え（reconcile_pia/rakuten/eplus）に置換済み"),
    ("2026-08-10", "drop", "reference_miyagi_event_sources",
     "冒頭から「events.html に宮城県の季節イベントを登録する際は」で始まる行楽専用の情報源3サイト。events.html はページごと廃止済み"),
    ("2026-08-10", "keep", "feedback_price",
     "クロスチェック系を廃止しても<b>価格だけは機械照合が代わりをやっていない</b>（reconcile系は販売日・枠・県を見るが価格は見ない）＝消すと空白になる"),
]
DONE_SLUGS = {d[2] for d in DONE}


def read(p):
    return open(p, encoding="utf-8", errors="replace").read()


playbook = read(PLAYBOOK) if os.path.exists(PLAYBOOK) else ""
index = read(os.path.join(MEM, "MEMORY.md"))

files = [f for f in sorted(os.listdir(MEM)) if f.endswith(".md") and f != "MEMORY.md"]

rows, linkcount = [], {}
docs = {}
for f in files:
    body = read(os.path.join(MEM, f))
    docs[f] = body
    for m in re.findall(r"\[\[([^\]]+)\]\]", body):
        linkcount[m.strip()] = linkcount.get(m.strip(), 0) + 1

for f in files:
    body = docs[f]
    slug = f[:-3]
    desc = ""
    m = re.search(r"^description:\s*(.*)$", body, re.M)
    if m:
        desc = m.group(1).strip().strip('"')
    typ = ""
    m = re.search(r"^\s*type:\s*(\w+)", body, re.M)
    if m:
        typ = m.group(1)
    mod = ""
    m = re.search(r"^\s*modified:\s*(\S+)", body, re.M)
    if m:
        mod = m.group(1)[:10]
    if not mod:
        mod = datetime.date.fromtimestamp(os.path.getmtime(os.path.join(MEM, f))).isoformat()
    rows.append({
        "slug": slug,
        "file": f,
        "type": typ or "?",
        "mod": mod,
        "chars": len(body),
        "links": linkcount.get(slug, 0),
        "pb": "○" if slug in playbook else "",
        "idx": "○" if slug in index else "",
        "desc": desc,
    })

# 捨てる候補ほど上に来るよう並べる（被リンク0→PLAYBOOK未掲載→古い順）
rows.sort(key=lambda r: (r["links"], r["pb"] == "○", r["idx"] == "○", r["mod"]))

total = len(rows)
orphan = sum(1 for r in rows if not r["links"] and not r["pb"] and not r["idx"])

tr = []
for i, r in enumerate(rows, 1):
    cls = "orphan" if (not r["links"] and not r["pb"] and not r["idx"]) else ""
    s = html.escape(r["slug"])
    mark = (
        '<td class="c mk">'
        '<button class="b keep" data-s="%s" data-v="keep">いる</button>'
        '<button class="b drop" data-s="%s" data-v="drop">いらない</button>'
        '<button class="b merge" data-s="%s" data-v="merge">統合</button>'
        "</td>" % (s, s, s)
    )
    badge = ' <span class="done">済</span>' if r["slug"] in DONE_SLUGS else ""
    tr.append(
        '<tr class="%s" data-slug="%s">%s<td>%d</td><td><a href="%s">%s</a>%s</td><td>%s</td><td>%s</td>'
        '<td class="n">%d</td><td class="n">%d</td><td class="c">%s</td><td class="c">%s</td><td>%s</td></tr>'
        % (cls, s, mark, i, html.escape(r["file"]), s, badge, html.escape(r["type"]),
           r["mod"], r["chars"], r["links"], r["pb"], r["idx"], html.escape(r["desc"]))
    )

# ── 処理済みの履歴ブロック ──────────────────────────────────
LAB = {"drop": "消した", "merge": "合わせた", "keep": "残した"}
done_rows = []
for date, verdict, slug, why in DONE:
    alive = os.path.exists(os.path.join(MEM, slug + ".md"))
    state = "（今もある）" if alive else "（削除済み）"
    done_rows.append(
        '<tr class="d-%s"><td class="c">%s</td><td class="c"><b>%s</b></td><td><code>%s</code></td>'
        '<td class="c">%s</td><td>%s</td></tr>'
        % (verdict, date, LAB[verdict], html.escape(slug), state, why)
    )
n_drop = sum(1 for d in DONE if d[1] == "drop")
n_merge = sum(1 for d in DONE if d[1] == "merge")
n_keep = sum(1 for d in DONE if d[1] == "keep")
done_html = (
    '<details id="done" open><summary>あたしが処理した分（%d件）　'
    '消した %d ／ 合わせた %d ／ 残した %d</summary>'
    '<p class="note">「合わせた」＝消す前に<b>後継のmemoryへ移した1行</b>を書いてあるわ。'
    'ここに出ているものはもう表には並んでいないから、判定しなくていい。</p>'
    '<table class="donetbl"><tr><th>日付</th><th>判定</th><th>memory</th><th>状態</th>'
    '<th>理由／移した1行</th></tr>%s</table></details>'
    % (len(DONE), n_drop, n_merge, n_keep, "\n".join(done_rows))
)

doc = """<!doctype html><html lang="ja"><head><meta charset="utf-8">
<title>OSHINAVI 保存memory 棚卸し表</title>
<style>
 body{font-family:"Segoe UI","Yu Gothic UI",sans-serif;margin:24px;color:#222;background:#fff}
 h1{font-size:20px;margin:0 0 6px}
 p.lead{color:#555;margin:0 0 16px;font-size:14px;line-height:1.7}
 table{border-collapse:collapse;width:100%%;font-size:13px}
 th,td{border:1px solid #ddd;padding:5px 7px;vertical-align:top}
 th{background:#f4f4f4;position:sticky;top:0}
 td.n,td.c{text-align:center;white-space:nowrap}
 tr.orphan{background:#fff6f6}
 a{color:#0645ad}
 .k{background:#fff6f6;border:1px solid #f0caca;padding:2px 6px;border-radius:3px}
 td.mk{white-space:nowrap}
 .b{font-size:11px;padding:2px 5px;margin:0 1px;border:1px solid #bbb;background:#fafafa;border-radius:3px;cursor:pointer}
 .b:hover{background:#eee}
 tr[data-mark="keep"]{background:#eefaee!important}
 tr[data-mark="drop"]{background:#ffecec!important;opacity:.72}
 tr[data-mark="merge"]{background:#fff8e0!important}
 tr[data-mark="keep"] .b.keep{background:#2e7d32;color:#fff;border-color:#2e7d32}
 tr[data-mark="drop"] .b.drop{background:#c62828;color:#fff;border-color:#c62828}
 tr[data-mark="merge"] .b.merge{background:#ef6c00;color:#fff;border-color:#ef6c00}
 #bar{position:sticky;top:0;z-index:5;background:#fff;padding:8px 0 10px;border-bottom:2px solid #ddd;margin-bottom:10px}
 #bar button{font-size:13px;padding:6px 12px;margin-right:8px;cursor:pointer}
 #out{width:100%%;height:150px;font-family:Consolas,monospace;font-size:12px;margin-top:8px;display:none}
 #cnt{font-size:13px;color:#444;margin-left:6px}
 #done{margin:0 0 16px;border:1px solid #ddd;border-radius:5px;padding:8px 12px;background:#fbfbfb}
 #done summary{cursor:pointer;font-weight:bold;font-size:14px}
 #done p.note{font-size:12px;color:#555;margin:8px 0}
 table.donetbl{font-size:12px;margin-top:6px}
 table.donetbl code{font-size:12px}
 tr.d-drop{background:#ffecec}
 tr.d-merge{background:#fff8e0}
 tr.d-keep{background:#eefaee}
 span.done{font-size:10px;background:#2e7d32;color:#fff;border-radius:3px;padding:1px 4px;margin-left:4px}
</style></head><body>
<h1>OSHINAVI 保存memory 棚卸し表（%d件）</h1>
<p class="lead">
「捨てる候補ほど上」に並べてあります。判断の目安は次の3つ。<br>
<b>被リンク</b>＝他のmemoryから <code>[[名前]]</code> で参照された回数。0なら孤立。<br>
<b>PB</b>＝PLAYBOOK.md（行動別チェックリスト）に載っているか。○なら日々の作業に直結。<br>
<b>索引</b>＝MEMORY.md（毎回読み込まれる一覧）に載っているか。<br>
<span class="k">赤い行</span>＝被リンク0・PLAYBOOK未掲載・索引未掲載＝<b>消しても誰も参照していない候補（%d件）</b>。<br>
名前をクリックすると本文が開きます。
</p>
%s
<div id="bar">
 <button id="copy">判定した分をコピー</button>
 <button id="clear">判定を全部消す</button>
 <span id="cnt"></span>
 <textarea id="out" readonly></textarea>
</div>
<table>
<tr><th>判定</th><th>#</th><th>名前</th><th>種類</th><th>最終更新</th><th>文字数</th><th>被リンク</th><th>PB</th><th>索引</th><th>説明</th></tr>
%s
</table>
<script>
const KEY='oshinavi_memory_audit';
let mk=JSON.parse(localStorage.getItem(KEY)||'{}');
function paint(){
  document.querySelectorAll('tr[data-slug]').forEach(tr=>{
    const v=mk[tr.dataset.slug];
    if(v){tr.setAttribute('data-mark',v);}else{tr.removeAttribute('data-mark');}
  });
  const n={keep:0,drop:0,merge:0};
  Object.values(mk).forEach(v=>n[v]++);
  document.getElementById('cnt').textContent=
    '判定済み '+Object.keys(mk).length+'件（いる '+n.keep+' / いらない '+n.drop+' / 統合 '+n.merge+'）　※ブラウザに自動保存。閉じても残るわ';
}
document.querySelectorAll('.b').forEach(b=>b.onclick=()=>{
  const s=b.dataset.s;
  if(mk[s]===b.dataset.v){delete mk[s];}else{mk[s]=b.dataset.v;}
  localStorage.setItem(KEY,JSON.stringify(mk));paint();
});
document.getElementById('copy').onclick=()=>{
  const lab={keep:'いる',drop:'いらない',merge:'統合'};
  const lines=[];
  ['drop','merge','keep'].forEach(v=>{
    const list=Object.keys(mk).filter(s=>mk[s]===v).sort();
    if(list.length){lines.push('【'+lab[v]+'】'+list.length+'件');list.forEach(s=>lines.push(s));lines.push('');}
  });
  const t=document.getElementById('out');
  t.style.display='block';t.value=lines.join('\\n')||'（まだ判定が無いわ）';
  t.select();try{document.execCommand('copy');}catch(e){}
};
document.getElementById('clear').onclick=()=>{
  if(confirm('判定を全部消すわよ。いい？')){mk={};localStorage.setItem(KEY,'{}');paint();
  document.getElementById('out').style.display='none';}
};
paint();
</script>
</body></html>""" % (total, orphan, done_html, "\n".join(tr))

open(OUT, "w", encoding="utf-8").write(doc)
print("memory %d件 / 孤立候補 %d件" % (total, orphan))
print("処理済み %d件（消した %d / 合わせた %d / 残した %d）" % (len(DONE), n_drop, n_merge, n_keep))
print("→ %s" % OUT)
