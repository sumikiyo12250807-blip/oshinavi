# -*- coding: utf-8 -*-
"""feedback_harvest_name_dedup_blindspot に e+ 側の同型事故（2026-09-05）を追記する。"""
import io, re, datetime

P = ('C:/Users/user/.claude/projects/C--Users-user-oshinavi/memory/'
     'feedback_harvest_name_dedup_blindspot.md')
s = io.open(P, encoding='utf-8').read()

ADD = """## 🚨🚨 2026-09-05 に **e+ 側でも同じ穴を踏んだ**（36候補 → 2件まで落ちた）

`tools/eplus_harvest.py` の `build` は、候補の `artist_key(title)` が
**DB全体の「artist+name」連結blobに部分一致したら捨てる**実装だった。
ぴあ側は2026-08-17に eventCd 判定へ直したのに、**e+ 側は名前判定のまま残っていた**。

**実測＝これから発売の候補36件のうち、eidでDBに実在したのは18件。残り18件は新規なのに、
名前の部分一致で16件が巻き添えで消え、投入できたのは2件だけだった。**
巻き添えの例＝**サーカス**（「メランコリックサーカス」に部分一致）／**wacci**／**シンギュラリティ**／
**Sick2**／**おとぎ話 / SCOOBIE DO**（"THE" で切れて何にでも当たる）。

✅**直した**＝重複判定は **eid（`/sf/detail/` の数字）が index.html にあるか**だけで行う。
名前がDBにある候補は**捨てずに残して**「同名別公演の可能性・投入前に突合」と警告を出す。旧挙動は `--name-dedup`。

🚨**教訓＝「名前が似ている」は捨てる根拠にならない。捨ててよいのは公演IDが同じ時だけ。**
同じ穴が別のハーベスタに残っていないか、直したら**必ず横展開して確かめる**
（ぴあ→e+→楽天→ローチケ）。→ [[feedback_check_existing_logic]]

### 同じ日に見つかった「部分一致で畳む」の逆側の事故
ぴあの `eventCd=2630866`（**サーカス**／加藤実・12/2 新宿文化センター）の販売枠が、
**id583「MELANCHOLIC CIRCUS」に混入していた**（「サーカス」⊂「メランコリックサーカス」）。
画面上は別アーティストの公演のチケットが売られている状態。→ 枠を外して別エントリに切り出した。
**畳む前に、飛び先URLのページ表題（＝ぴあ/e+が名乗っている公演名）を必ず開いて突き合わせる。**

---

"""

anchor = '## ✅ 2026-08-17 に道具を直した'
assert anchor in s, 'anchor not found'
s = s.replace(anchor, ADD + anchor, 1)
s = re.sub(r'^  modified: .*$',
           '  modified: %sT00:00:00.000Z' % datetime.date.today().isoformat(),
           s, count=1, flags=re.M)
io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('MEMORY_PATCHED')
