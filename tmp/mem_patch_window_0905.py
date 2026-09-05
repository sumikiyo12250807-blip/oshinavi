# -*- coding: utf-8 -*-
"""feedback_capture_all_deadlines_on_add に「登録済みの中で窓が増える型」を追記する。"""
import io, re, datetime

MEM = 'C:/Users/user/.claude/projects/C--Users-user-oshinavi/memory/'
P = MEM + 'feedback_capture_all_deadlines_on_add.md'
s = io.open(P, encoding='utf-8').read()

ADD = """## 🚨🚨【2026-09-05】**「買えるのに載っていない」＝登録済みエントリの中で販売窓が増える型**

`buy` の取りこぼしを探すとき、いつもは「**index.html に無いページ**」を探している。
その方法では **すでに載っているエントリの中で窓が増えた分**は**絶対に見つからない**。

実例＝**id5766 EPO 東京9/29**
- 既存（ぴあ由来）＝ 一般発売 **〜9/13 23:59** の1枠だけ
- e+ の実ページ＝ **〜9/20 18:00** と **〜9/25 18:00** の2枠が生きていた
→ **9/13を過ぎたらOSHINAVIでは買えない扱いになるのに、実際は9/25まで買えた**。

🚨これは [[feedback_zero_badge_gate]]（カードは出るのに買える枠0）の**裏返し**で、
**ゲートが1つも無い**（枠が「0」ではなく「少ない」ので何も鳴らない）。

✅**やること＝同名の既存がある候補は、公演の有無でなく「(県, M/D公演, 締切日)」まで比べる。**
- 同じ (県, M/D, 締切日) がある → 同じ販売窓。足さない（売り場が違うだけ）
- **締切日が違う → 別の販売窓＝取りこぼし。足す**
- 既存の枠は消さない。`url` が空の時だけ会場別URLを焼き込む（[[feedback_tour_per_ticket_url]]）
- ⚠️[[feedback_dedup_badges_keeps_urls]] は「**既存のバッジを畳む(消す)な**」であって
  「売り場が違えばコピーを足せ」ではない。買い口は [[feedback_vendor_priority]] のとおり1つでよい

📌県名の正規化の罠＝「東京都→東京」と同じ処理を「京都」にかけると「**京**」になって突合が外れる。
**剥がした結果が県名リストに無ければ剥がさない**こと。

---

"""

anchor = '新着エントリを追加する時点で、'
assert anchor in s, 'anchor not found'
s = s.replace(anchor, ADD + anchor, 1)
s = s.replace(
    'description: 【何度も再発】新着追加時に買える枠を1つ残らず展開。',
    'description: 【何度も再発】新着追加時に買える枠を1つ残らず展開。登録済みエントリでも「締切日が違う窓」は取りこぼし＝足す。',
    1)
if 'modified:' in s:
    s = re.sub(r'^  modified: .*$', '  modified: %sT00:00:00.000Z' % datetime.date.today().isoformat(),
               s, count=1, flags=re.M)
else:
    s = s.replace('  originSessionId: d35857a6-1912-45a6-8457-25010793f934',
                  '  originSessionId: d35857a6-1912-45a6-8457-25010793f934\n  modified: %sT00:00:00.000Z'
                  % datetime.date.today().isoformat(), 1)
io.open(P, 'w', encoding='utf-8', newline='\n').write(s)

# 索引の要約行も同じターンで直す
IP = MEM + 'MEMORY.md'
t = io.open(IP, encoding='utf-8').read()
OLD = '[新着追加時に買える枠を1つ残らず展開](feedback_capture_all_deadlines_on_add.md)（抽選結果発表を受付開始と誤読しない）'
NEW = ('🚨[新着追加時に買える枠を1つ残らず展開](feedback_capture_all_deadlines_on_add.md)'
       '（抽選結果発表を受付開始と誤読しない／**登録済みでも「締切日が違う窓」は取りこぼし＝足す**）')
assert OLD in t, 'index line not found'
io.open(IP, 'w', encoding='utf-8', newline='\n').write(t.replace(OLD, NEW, 1))
print('PATCHED_BOTH')
