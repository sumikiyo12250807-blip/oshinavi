# -*- coding: utf-8 -*-
"""「今週のピックアップ」のセクションHTMLを、差し込む前に機械で検品する（恒久ツール・2026-09-04 新設）。

出典＝[[project_weekly_pickup_article]] の「号を組むとき必ずこの順で確かめる」8項目。
2026-08-30 の号でこの8つを全部踏んだので、目視でなく機械で見る形にした。

  python tools/check_pickup.py tmp/pickup0906/section.html

終了コード 0＝合格 / 2＝要修正 / 3＝ファイルが読めない
"""
import io, os, re, sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SRC = sys.argv[1] if len(sys.argv) > 1 else "tmp/pickup0906/section.html"
if not os.path.exists(SRC):
    print("ファイルが無い: %s" % SRC); sys.exit(3)
s = io.open(SRC, encoding="utf-8", newline="").read()
idx = io.open("index.html", encoding="utf-8", newline="").read()

ng = []
ok = []


def check(cond, good, bad):
    (ok if cond else ng).append(good if cond else bad)


# 1. pk-most を本文の箱に使っていないか（小さな赤バッジ専用。divで使うと記事全体が赤地に黒字11pxになる）
check("<div class=\"pk-most\"" not in s,
      "pk-most を本文の箱に使っていない",
      "🚨pk-most を <div> で使っている＝記事が赤地・黒字・11pxになる（本文は pk-act + pk-detail）")

# 2. blockquote（pk- のCSSが無い。引用は普通の <p> で「」を付ける）
check("<blockquote" not in s, "blockquote なし", "🚨blockquote を使っている（pk-のCSSが無いので崩れる）")

# 3. マークダウンの残骸
check("&gt;" not in s, "&gt; の残骸なし", "🚨マークダウンの > が &gt; のまま残っている")
check("|---" not in s, "表の残骸なし", "🚨マークダウンの表 |--- が本文に残っている")

# 4. 閉じるボタン
check('id="pickupClose"' in s, "id=pickupClose がある",
      "🚨id=\"pickupClose\" が無い＝開いたあと閉じる手段が画面から消える")
n_act = len(re.findall(r"class=\"pk-act", s))  # pk-act pk-top も数える
n_shut = len(re.findall(r"data-pk-shut", s))
check(n_shut >= n_act,
      "data-pk-shut %d ≧ pk-act %d" % (n_shut, n_act),
      "🚨data-pk-shut(%d) が pk-act(%d) より少ない＝閉じられないカードがある" % (n_shut, n_act))

# 5. ▲を文字で書いていないか（CSSの ::after が足すので二重になる）
check("▲" not in s and "▼" not in s,
      "▲▼ を文字で書いていない",
      "🚨▲か▼を文字で書いている＝CSSの ::after と二重になる")

# 6. 締めの形
check('<a class="pk-tail"' in s and 'class="pk-go">今週発売を見る →</span>' in s,
      "締めが pk-tail ＋「今週発売を見る →」の形",
      "🚨締めが <a class=\"pk-tail\">…<span class=\"pk-go\">今週発売を見る →</span></a> の形になっていない")

# 7. 使っているクラスが index.html の <style> に定義されているか
used = set(re.findall(r'class="([^"]+)"', s))
cls = set()
for u in used:
    for c in u.split():
        if c.startswith("pk-"):
            cls.add(c)
style = idx[idx.find("<style"):idx.find("</style>")]
undef = sorted(c for c in cls if ("." + c) not in style)
check(not undef, "使っている pk- クラス %d 個は全部 index.html に定義済み" % len(cls),
      "🚨index.html の <style> に無いクラス: %s" % "／".join(undef))

# 8. 「。」のあとが全部 <br> か（apply_pickup.py がここで落ちる）
body = re.sub(r"<[^>]+>", "\x00", s)
bad = []
for m in re.finditer(r"。", s):
    tail = s[m.end():m.end() + 4]
    if tail.startswith("<br") or tail.startswith("</p>") or tail.startswith("</a") or tail.startswith("</s"):
        continue
    # 締めの固定文「…わよ。<span class="pk-go">今週発売を見る →</span>」は正しい形
    if s[m.end():m.end() + 22].startswith('<span class="pk-go"'):
        continue
    if tail.startswith("」") or tail.startswith("）") or tail.startswith("</"):
        continue
    bad.append(s[max(0, m.start() - 24):m.end() + 8].replace("\n", " "))
check(not bad, "「。」のあとは全部改行されている",
      "🚨「。」のあとが改行されていない箇所 %d 件: %s" % (len(bad), " ／ ".join(bad[:3])))

# 追加：封印フレーズ（[[feedback_x_phrase_blacklist]]）
for w in ("生で浴びる",):
    check(w not in s, "封印フレーズ「%s」なし" % w, "🚨封印フレーズ「%s」が入っている" % w)

# 追加：二人称（記事は二人称を使わない）
check("あなた" not in s, "二人称「あなた」なし", "⚠️「あなた」が入っている（記事は二人称を使わない）")

print("=== 今週のピックアップ 検品: %s ===" % SRC)
for o in ok:
    print("  ✅ %s" % o)
for x in ng:
    print("  %s" % x)
print()
if ng:
    print("🚨要修正 %d件" % len(ng)); sys.exit(2)
print("✅全項目パス"); sys.exit(0)
