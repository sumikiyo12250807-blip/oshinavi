# -*- coding: utf-8 -*-
"""project_eplus_harvester_bug_and_qc に 2026-09-05 の実測を追記する。"""
import io, re, datetime

MEM = 'C:/Users/user/.claude/projects/C--Users-user-oshinavi/memory/'
P = MEM + 'project_eplus_harvester_bug_and_qc.md'
s = io.open(P, encoding='utf-8').read()

ADD = """## 🚨🚨【2026-09-05 実測】**`gate_eplus_slots` が PASS しても `reconcile_eplus` は151件FAIL する**

受付中ぶん49エントリをビルド → `gate_eplus_slots` **PASS** → 投入 →
`reconcile_eplus --ids`（48エントリ・271枠）で **FAIL 151件**。
内訳＝**c-死枠 114** ／ a-締切>公演日 16 ／ b-締切ズレ 8 ／ b-発売日ズレ 5 ／ b-締切時刻ズレ 4 ／ h-時刻欠 3 ／ b-発売前化 1。

**真因＝上に何年も書いてある「buildの-P直取り化が未実装」そのもの。**
e+のツアーは**個別の -P ページに販売窓を出さないことがある**のに、build は
**base ページの窓を各公演にコピーして**付ける。だから -P ページを見にいく reconcile が「窓が無い」と弾く。
そのまま載せると **バッジを押しても買えないページに着く**。

🚨**`gate_eplus_slots` は「実ページの枠 < ビルドの枠」を NOTE で流していた（33本）＝ゲートが静かに見逃す作り。**
　PASS を信じて投入したのが今回の失敗。**ゲートは2枚とも通す**（gate → 投入 → reconcile → FAILを落とす）。
　できれば `gate_eplus_slots` の NOTE を **件数がしきい値を超えたら FAIL** に変える。

**後始末の型（今回やったこと）**
- FAILの枠だけを **index 指定で抜く**。バックアップで丸ごと戻さない（別セッションの追記が消えるため）
- 既存へ足した分は「投入前の本数より後ろ」だけが自分の追加＝**そこだけ抜く。元からある枠は触らない**
- 結果＝133枠を落として **FAIL 0**。落としたエントリ0件（枠が0本になったものは無かった）

📌**券種名を潰す穴は e+ 側にもある**（[[feedback_pia_parser_flattens_slots]] と同型）＝
`id6979 New Acoustic Camp 2026` は実ページに「先着一般発売 2026-07-16〜2026-09-18」が
**まったく同じ文言で2〜3行**あり、ビルドが1本に潰していた（券種違いが画面から消える）。**投入しない**で保留。

📌**url の焼き込みは「同じ売り場から取ったラベル」にだけ**＝
id5784 ORCALAND の ぴあ由来ラベル（〜9/10 **23:59**）に e+ の -P URL を焼いたら、
実ページの締切（**18:00**）と食い違って [b-締切時刻ズレ] で弾かれた。**他社URLを付けると押した先の締切が変わる**。

---

"""

anchor = '【e+ハーベスタの系統バグ＝根本原因と防止システム'
assert anchor in s, 'anchor not found'
s = s.replace(anchor, ADD + anchor, 1)
s = re.sub(r'^  modified: .*$', '  modified: %sT00:00:00.000Z' % datetime.date.today().isoformat(),
           s, count=1, flags=re.M)
io.open(P, 'w', encoding='utf-8', newline='\n').write(s)

IP = MEM + 'MEMORY.md'
t = io.open(IP, encoding='utf-8').read()
OLD = '🚨[ハーベスタの系統バグとQCゲート設計](project_eplus_harvester_bug_and_qc.md)'
NEW = ('🚨🚨[ハーベスタの系統バグとQCゲート設計](project_eplus_harvester_bug_and_qc.md)'
       '（**gate_eplus_slotsがPASSしてもreconcile_eplusは151件FAILする＝2枚とも通す**・2026-09-05実測）')
assert OLD in t, 'index line not found'
io.open(IP, 'w', encoding='utf-8', newline='\n').write(t.replace(OLD, NEW, 1))
print('PATCHED_BOTH')
