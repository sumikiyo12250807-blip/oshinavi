# -*- coding: utf-8 -*-
"""4491 石川さゆりコンサート ～極上のアンサンブル～（三重・響ホール伊勢 2027/1/30）を消す。

ユーザー判断（2026-09-06 夜）＝「①」。あたしは「発売日未定に直して残す」を勧めたが、
ユーザーが消すと決めた。

【なぜ DELETE_GATE の除外条件（公演が未来）に当たるのに消すか】
- 公演自体は本当にある（会場公式に 2027/1/30・2回公演・料金まで出ている）
  https://www.ise-kanbun.jp/event/44399/
- でも **買える売り場が今どこにも無い**
  ・ぴあ eventCd=2628224 は「ご指定の公演情報が見つかりませんでした」＝死亡（実ページで確認）
  ・pia_kw_search で石川さゆりを総ざらいしても、三重の公演は10件のどこにも出てこない
  ・会場公式が「**発売日は変更予定・現在調整中**」と明記＝発売日そのものが取り消されている
- 登録には「一般発売（三重 R9年 1/30公演）**9/12 10:00発売**」が入ったまま
  ＝**嘘の発売日を表示し続ける**（OSHINAVIでいちばんやってはいけないこと）

発売日が決まれば、ぴあの発売前スイープで自然に拾い直せる。
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

APPLY = "--apply" in sys.argv
TARGET = 4491

h = open("index.html", encoding="utf-8").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))

hit = next((e for e in EVENTS if e["id"] == TARGET), None)
if not hit:
    print("見つからない id=%d" % TARGET)
    sys.exit(1)

print("消す id=%d %s" % (hit["id"], hit.get("artist")))
print("  会場   %s（%s）" % (hit.get("venue"), hit.get("prefecture")))
print("  公演日 %s" % hit.get("date"))
print("  ぴあ   %s ← 死亡（ご指定の公演情報が見つかりませんでした）"
      % ((hit.get("links") or {}).get("pia")))
for t in hit.get("tickets") or []:
    print("  枠     %s （〜%s）" % (t.get("type"), t.get("date")))

kept = [e for e in EVENTS if e["id"] != TARGET]
print("")
print("EVENTS %d件 → %d件" % (len(EVENTS), len(kept)))

if APPLY:
    open("index.html.bak_0906_ishikawa", "w", encoding="utf-8").write(h)
    new_arr = json.dumps(kept, ensure_ascii=False, indent=2)
    out = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]
    mo = re.search(r"(  const NEW_ORDER = \[)([^\]]*)(\];)", out)
    ids = [int(x) for x in mo.group(2).replace("\n", "").split(",") if x.strip()]
    left = [i for i in ids if i != TARGET]
    out = out[:mo.start()] + mo.group(1) + ", ".join(str(i) for i in left) + mo.group(3) + out[mo.end():]
    open("index.html", "w", encoding="utf-8").write(out)
    with open("logs/removed_2026-09-06.md", "a", encoding="utf-8") as f:
        f.write("\n## 追加の削除（夜・ユーザー判断）\n\n")
        f.write("| id | 公演名 | 会場 | 公演日 | 確認用URL |\n|---|---|---|---|---|\n")
        f.write("| 4491 | 石川さゆりコンサート ～極上のアンサンブル～ | シンフォニアテクノロジー響ホール伊勢 大ホール | 2027-01-30 | https://www.ise-kanbun.jp/event/44399/ |\n")
        f.write("\n公演自体は会場公式にある（2027/1/30・2回公演・一般7,000円）が、\n")
        f.write("**買える売り場が今どこにも無い**＝ぴあ eventCd=2628224 は死亡、\n")
        f.write("pia_kw_search の10件にも三重は出ず、会場公式は「発売日は変更予定・現在調整中」。\n")
        f.write("登録には「9/12 10:00発売」が残っていた＝**嘘の発売日を表示していた**ので消した。\n")
        f.write("🚨発売日が決まれば発売前スイープで自然に拾い直せる。\n")
    print("書き込み完了 (backup: index.html.bak_0906_ishikawa / logs/removed_2026-09-06.md に追記)")
else:
    print("（--apply で書き込む）")
