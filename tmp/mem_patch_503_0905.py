# -*- coding: utf-8 -*-
"""reference_pia_rate_limit_429 に e+ の 503（同じ型）を追記し、要約行も直す。"""
import io, re, datetime

MEM = 'C:/Users/user/.claude/projects/C--Users-user-oshinavi/memory/'
P = MEM + 'reference_pia_rate_limit_429.md'
s = io.open(P, encoding='utf-8').read()

ADD = """## 🚨🚨【2026-09-05】**e+ にも同じ型がある＝HTTP 503 Service Unavailable**

`reconcile_eplus.py` が **[FETCH] ページ取得失敗** を出した枠（id6938 シンギュラリティの東京10/7
`https://eplus.jp/sf/detail/4589180001-P0030001P021001`）を、間をあけて単発で叩き直したら
**HTTP 200・JSON-LDも公演日も正常**だった。＝**URLは生きていて、503で照合できなかっただけ**。

真因＝**同じ時間帯に別セッションが e+ の一括ビルド（候補58件）を走らせていた**。
`eplus_harvest.fetch()` は4回リトライするが、並列で叩いていると**4回とも503を踏む**。

🚨**[FETCH] は「枠が死んだ」ではなく「照合できなかった」。時間をあけて取り直すまで判定を確定しない。**
ぴあの429／sorry.pia と**まったく同じ構造**で、**QCゲートが静かに壊れる**。
- 報告は必ず「照合できた枠／FETCHで照合できなかった枠」を分ける（[[feedback_coverage_not_count]]）
- e+ の一括ビルド中は `reconcile_eplus` を回さない。**順番に流す**
- 切り分けの型＝`tmp/url_probe_0905.py`（同じURLを8秒あけて3回・比較用に通っている枠も一緒に叩く）

---

"""

anchor = '## 🚨🚨【2026-08-06・「静かな0」の正体が判明'
assert anchor in s, 'anchor not found'
s = s.replace(anchor, ADD + anchor, 1)
s = s.replace(
    'description: ぴあは連続アクセスで HTTP 429 を返す→reconcile が「買える枠0」と読み STALE を大量誤検知する。QCゲートが静かに効かなくなる型',
    'description: 連続アクセスでぴあは429/sorry・e+は503を返す→reconcileが「買える枠0」「取得失敗」と読み、QCゲートが静かに効かなくなる型',
    1)
s = re.sub(r'^  modified: .*$',
           '  modified: %sT00:00:00.000Z' % datetime.date.today().isoformat(),
           s, count=1, flags=re.M)
io.open(P, 'w', encoding='utf-8', newline='\n').write(s)

# 索引の要約行も同じターンで直す（feedback_rules_one_place_and_fix_summaries）
IP = MEM + 'MEMORY.md'
t = io.open(IP, encoding='utf-8').read()
OLD = '🚨[429でQCゲートが静かに壊れる](reference_pia_rate_limit_429.md)'
NEW = '🚨🚨[叩きすぎるとQCゲートが静かに壊れる](reference_pia_rate_limit_429.md)（ぴあ429/sorry・**e+503も同型**＝FETCHは「枠が死んだ」でなく「照合できなかった」）'
assert OLD in t, 'index line not found'
io.open(IP, 'w', encoding='utf-8', newline='\n').write(t.replace(OLD, NEW, 1))
print('PATCHED_BOTH')
