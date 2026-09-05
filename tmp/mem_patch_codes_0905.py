# -*- coding: utf-8 -*-
"""feedback_pia_parser_flattens_slots の「売り場コードで数える」節に、もう1つの穴を足す。"""
import io, re, datetime

MEM = 'C:/Users/user/.claude/projects/C--Users-user-oshinavi/memory/'
P = MEM + 'feedback_pia_parser_flattens_slots.md'
s = io.open(P, encoding='utf-8').read()

ADD = """
### 🚨【2026-09-05】もう1つの穴＝**終了した売り場のコードも数に入る**

2026-09-03項は「**発売前**の枠はコードを持たないので数えられない」だったけど、逆側もある＝
**受付終了・予定枚数終了の枠のコードもページに残っている**。だから
**「コードのユニーク数」は"今買える枠の数"ではない**。引き算の材料にすると必ずズレる。

実測＝**id2254 杉山清貴**（ぴあURL14本）
- 売り場コードのユニーク数 **24個** ／ 販売スケジュール行 **62件**
- その62件を状態で仕分けると **買える13 / 買えない49**
- 買える13行から「bundleと個別eventCdが同じ公演を二重に出す」分を外すと **8種類**
- 登録19枠と突き合わせると、**足りないのは1枠だけ**だった
  （「ぴあカードで確率UP」と「当選確率アップ」の**3次受付が2券種**あるのに、`kenshu()` が
  両方「3次受付」に潰すので `merge_apply` が足さない）

✅**数え方の順番**＝①生HTMLの販売スケジュール行を全部取る ②**状態で「買える／買えない」に仕分ける**
③bundleと個別eventCdの重複を外す ④そこで初めて登録と突き合わせる。
雛形＝`tmp/count_2254_0905.py`（コードと行を両方取る）＋`tmp/classify_2254_0905.py`（状態で仕分ける）。

📌**逆側も見る**＝登録にあるのに「買える行」に出てこない枠は、売り切れたのか
ヒール前で締切が入っていないだけなのか分からない。**`tools/pia_statustext.py` で状態テキストを直に読む**。

"""

anchor = '## 🚨【2026-09-03】**「売り場コードのユニーク数」で数えられるのは"受付中"の枠だけ**'
assert anchor in s, 'anchor not found'
i = s.index(anchor)
# 2026-09-03 の節の末尾（ファイル末）に足す
s = s.rstrip('\n') + '\n' + ADD
s = re.sub(r'^  modified: .*$', '  modified: %sT00:00:00.000Z' % datetime.date.today().isoformat(),
           s, count=1, flags=re.M)
io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('PATCHED')
