# -*- coding: utf-8 -*-
"""第2便（e+の受付中ぶん）を logs に追記する。"""
import json, io, re, datetime

TODAY = datetime.date.today().isoformat()
P = 'logs/newpool_%s_eplus.md' % TODAY
hh = io.open('index.html', encoding='utf-8', newline='').read()
db = {e['id']: e for e in json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);', hh, re.S).group(1))}

L = ['\n---\n', '# 第2便＝e+の「受付中」ぶん（同じ日の午前）\n']
L.append('候補180件 → 公演IDでDBに実在した122件を除外 → 58件をビルド → 49エントリ。')
L.append('そのうち **公演が全部すでに載っていた6件は投入せず**、')
L.append('**同じアーティストのツアーが既にある4件は新規を作らず既存に足りない枠だけ足し**、残りを新規で投入。\n')
L.append('## 機械ゲートの結果（🚨2枚とも通さないと素通りする）\n')
L.append('| ゲート | 結果 |')
L.append('|---|---|')
L.append('| `gate_eplus_slots` | **PASS**（エントリ49件・照合したURL184本） |')
L.append('| `reconcile_eplus --ids`（48件・271枠） | 🚨 **FAIL 151件**（c-死枠114／a-締切>公演日16／b-締切ズレ8／b-発売日ズレ5／b-締切時刻ズレ4／h-時刻欠3／b-発売前化1） |')
L.append('| 後始末＝FAILの枠133本を落とす | `reconcile_eplus` 再照合 **FAIL 0**（134枠） |')
L.append('| `check_badges` / `check_order` / `check_dup_slots` | OK ／ 違反0 ／ **A0・B0・C0** |')
L.append('| CRLF指紋 | 全行CRLF・LF単独0 |\n')
L.append('🚨**`gate_eplus_slots` が PASS しても安心できない。**')
L.append('e+のツアーは**個別の -P ページに販売窓を出さないことがある**のに、')
L.append('`eplus_harvest.py build` は **base ページの窓を各公演にコピー**する。')
L.append('ゲート側はそれを「実ページの枠 < ビルドの枠」の **NOTE で流していた**（33本）。')
L.append('そのまま載せると**バッジを押しても買えないページに着く**ので、reconcile が弾いた分は落とした。\n')

order = [int(x) for x in re.findall(r'\d+', re.search(r'NEW_ORDER\s*=\s*\[([0-9,\s]*)\]', hh).group(1))]
new_ids = [i for i in order if 6948 <= i <= 6985]
L.append('## 新着に入れた%d件（id6948〜6985）\n' % len(new_ids))
L.append('| id | 出演 | 公演名 | 会場 | 公演日 | 枠 | 確認用 |')
L.append('|---|---|---|---|---|---|---|')
for i in new_ids:
    e = db.get(i)
    if not e:
        continue
    url = (e.get('links') or {}).get('eplus') or ''
    L.append('| %d | %s | %s | %s | %s | %d | [ページ](%s) |'
             % (i, e['artist'], e['name'], e['venue'], e['date'], len(e['tickets']), url))

L.append('\n## 既存ツアーに足した枠（新規エントリを作らなかった分）\n')
L.append('| id | 公演名 | 足した枠 |')
L.append('|---|---|---|')
for tid in (5879, 5251, 5784, 5766, 3892, 1477, 2325, 4240, 5762, 579):
    e = db.get(tid)
    if e:
        L.append('| %d | %s ／ %s | 枠合計 %d本 |' % (tid, e.get('artist'), e.get('name'), len(e['tickets'])))

L.append("""
## 投入しなかったもの（理由つき）

| 何 | 理由 |
|---|---|
| セカンドバッカー／栄喜／リュックと添い寝ごはん／ORCALAND／水平線 | **公演が全部すでに載っていた**（(県, M/D公演) の重なり100%） |
| New Acoustic Camp 2026 | `gate_eplus_slots` FAIL＝実ページに**まったく同じ文言の券種が2〜3行**あり、ビルドが1本に潰していた。券種違いが画面から消えるので**保留** |
| FAILした133枠 | -Pページに販売窓が無い（押しても買えない） |

## 🚨 この便で見つけた取りこぼし

**id5766 EPO の東京9/29**＝既存（ぴあ）は一般発売 **〜9/13 23:59** の1枠だけ。
e+ の実ページには **〜9/20 18:00** と **〜9/25 18:00** の2枠が生きていた。
＝**9/13を過ぎたら画面上は買えないのに、実際は9/25まで買えた**。この2枠を足した。

「公演が載っているか」だけ見ると見逃す型。**販売窓の終わりまで比べる**こと。

## 🚨 url の焼き込みで踏んだ罠

**id5784 ORCALAND** の ぴあ由来ラベル（〜9/10 **23:59**）に e+ の -P URL を焼いたら、
実ページの締切（**18:00**）と食い違って `[b-締切時刻ズレ]` で弾かれた。**4本とも外した**。
＝**url の焼き込みは「同じ売り場から取ったラベル」にだけ**。他社URLを付けると押した先の締切が変わる。
""")

io.open(P, 'a', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')
print('APPENDED %s (新規%d件)' % (P, len(new_ids)))
