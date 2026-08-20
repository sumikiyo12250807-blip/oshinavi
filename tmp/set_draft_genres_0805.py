# -*- coding: utf-8 -*-
"""相談分のジャンルを下書き(_genre/_extraGenres)に反映する（ユーザー「全部あなたの案でOK」2026-08-05）。

  3686 メトロ怪談×北野誠の茶屋町怪談  engeki  → kaidan （新ジャンル・8/4夜の指示）
  3736 リニアクラシックコンサート      fes     → classic（屋内ホールの単独クラシック＝フェスでない）
  3769 流白浪燦星(ルパン三世 南座)      dento   → dento + extra:anime
  3753 岡山子ども未来ミュージカル       musical → musical + extra:kids
  （3733 岡崎ジャズストリートは jazz のまま＝変更なし）

🚨 genre は "new" のまま動かさない＝プールの件数を1件も変えない（[[feedback_new_pool_ok_before_assign]]）。
   実際の振り分けはユーザーが「振り分けて」と言ってから。
index.html はバイナリで行単位に扱いCRLFを保つ（[[feedback_index_html_crlf_preserve]]）。
"""
import io
import os
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P = r"C:\Users\user\oshinavi\index.html"
BAK = r"C:\Users\user\oshinavi\index.html.bak_0805_draft_genres"

# id: (新しい_genre, 新しい_extraGenres)
PLAN = {
    3686: ("kaidan", []),
    3736: ("classic", []),
    3769: ("dento", ["anime"]),
    3753: ("musical", ["kids"]),
}

b = open(P, "rb").read()
crlf0, lf0 = b.count(b"\r\n"), b.count(b"\n")
print("修正前: CRLF %d / 単独LF %d" % (crlf0, lf0 - crlf0))
if not os.path.exists(BAK):
    shutil.copyfile(P, BAK)

lines = b.split(b"\r\n")
done = {}
for i, ln in enumerate(lines):
    t = ln.decode("utf-8", "replace").strip()
    if not t.startswith('"id": '):
        continue
    try:
        eid = int(t[6:].rstrip(","))
    except ValueError:
        continue
    if eid not in PLAN:
        continue
    g, ex = PLAN[eid]
    hit_g = hit_e = False
    for j in range(i, min(i + 30, len(lines))):
        s = lines[j].decode("utf-8", "replace")
        if '"_genre":' in s and not hit_g:
            old = s.split('"_genre":')[1].strip().rstrip(",").strip('"')
            lines[j] = ('    "_genre": "%s",' % g).encode("utf-8")
            hit_g = True
            print("  id%d _genre %s → %s" % (eid, old, g))
        elif '"_extraGenres":' in s and not hit_e:
            body = ", ".join('"%s"' % x for x in ex)
            lines[j] = ('    "_extraGenres": [%s],' % body).encode("utf-8")
            hit_e = True
            print("  id%d _extraGenres → [%s]" % (eid, body))
        elif '"genre": "new"' in s and j > i and hit_g and hit_e:
            break
    done[eid] = (hit_g, hit_e)

miss = [k for k in PLAN if done.get(k) != (True, True)]
if miss:
    print("\n🚨 見つからなかったid: %s（1文字も書き込まない）" % miss)
    sys.exit(1)

nb = b"\r\n".join(lines)
crlf1, lf1 = nb.count(b"\r\n"), nb.count(b"\n")
assert lf1 - crlf1 == 0, "単独LFが混入した"
open(P, "wb").write(nb)
print("\n✅ %d件の下書きを更新（genreは全部 new のまま）" % len(PLAN))
print("修正後: CRLF %d / 単独LF %d" % (crlf1, lf1 - crlf1))
