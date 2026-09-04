# -*- coding: utf-8 -*-
"""ジャンル「イベント」（event）を おでかけ グループに新設する。
ユーザー指示 2026-09-04「お出かけにイベントのジャンル作ってそれに入れて」

🚨ジャンルを1つ増やす時に触るのは5か所（[[feedback_genre_pia_asis_and_other]]／
   [[feedback_dento_split_music_stage]]＝1か所でも抜けると画面が壊れる）
  1. index.html の GENRE_LABEL（表示名）
  2. index.html の GENRE_GROUPS.odekake（入れないと「おでかけすべて」で消える）
  3. index.html のフィルターボタン
  4. index.html の CSS .genre-event（バッジの色）
  5. tools/build_ai_page.py の GENRE_LABEL（無いと ai.html に生の event が出る）

あわせて id6397「Good Morning Record Bar Presents『GOOD DAY KYOTO』」を event にする。

  python tmp/add_genre_event_0904.py          # 下見
  python tmp/add_genre_event_0904.py --apply  # 実行
"""
import io, re, sys, json, shutil

APPLY = "--apply" in sys.argv
COLOR = "#a1887f"          # 既存に無いブラウン系
RGB = "161,136,127"

h = io.open("index.html", encoding="utf-8", newline="").read()
ai = io.open("tools/build_ai_page.py", encoding="utf-8", newline="").read()
done = []

# ── 1. GENRE_LABEL
a1 = '    talkshow: "トークショー"\n  };'
b1 = ('    talkshow: "トークショー",\n'
      '    /* 2026-09-04 ユーザー「お出かけにイベントのジャンル作ってそれに入れて」\n'
      '       ＝複数組が出るイベント型の催しを、音楽の棚でなく おでかけ で探せるようにした。 */\n'
      '    event: "イベント"\n  };')
if 'event: "イベント"' in h:
    done.append("1 GENRE_LABEL … すでにある")
elif a1.replace("\n", "\r\n") in h:
    h = h.replace(a1.replace("\n", "\r\n"), b1.replace("\n", "\r\n"), 1); done.append("1 GENRE_LABEL 追加")
elif a1 in h:
    h = h.replace(a1, b1, 1); done.append("1 GENRE_LABEL 追加")
else:
    print("ABORT: GENRE_LABEL の差し込み位置が見つからない"); sys.exit(1)

# ── 2. GENRE_GROUPS.odekake
a2 = 'odekake: ["sports","art","kids","fes","hanabi","gourmet","gakusai"]'
b2 = 'odekake: ["sports","art","kids","fes","hanabi","gourmet","gakusai","event"]'
if b2 in h:
    done.append("2 GENRE_GROUPS … すでにある")
elif a2 in h:
    h = h.replace(a2, b2, 1); done.append("2 GENRE_GROUPS.odekake 追加")
else:
    print("ABORT: GENRE_GROUPS.odekake が見つからない"); sys.exit(1)

# ── 3. フィルターボタン（学園祭の隣に置く）
a3 = '<button class="filter-btn" data-genre="gakusai">学園祭</button>'
b3 = a3 + '<button class="filter-btn" data-genre="event">イベント</button>'
if 'data-genre="event"' in h:
    done.append("3 フィルターボタン … すでにある")
elif a3 in h:
    h = h.replace(a3, b3, 1); done.append("3 フィルターボタン 追加")
else:
    print("ABORT: 学園祭のフィルターボタンが見つからない"); sys.exit(1)

# ── 4. CSS
a4 = re.search(r"( *)\.genre-gakusai[^\n]*\n", h)
if ".genre-event" in h:
    done.append("4 CSS … すでにある")
elif a4:
    ind = a4.group(1)
    css = ("%s.genre-event      { background: rgba(%s,0.15); color: %s;       "
           "border: 1px solid rgba(%s,0.35); }\n" % (ind, RGB, COLOR, RGB))
    if "\r\n" in h:
        css = css.replace("\n", "\r\n")
    h = h[:a4.end()] + css + h[a4.end():]
    done.append("4 CSS .genre-event 追加")
else:
    print("ABORT: .genre-gakusai のCSSが見つからない"); sys.exit(1)

# ── 5. build_ai_page.py の GENRE_LABEL
if '"event"' in ai and "イベント" in ai:
    done.append("5 build_ai_page … すでにある")
else:
    m5 = re.search(r'("talkshow"\s*:\s*"トークショー")', ai)
    if not m5:
        print("ABORT: build_ai_page.py の GENRE_LABEL に talkshow が見つからない"); sys.exit(1)
    ai = ai[:m5.end()] + ', "event": "イベント"' + ai[m5.end():]
    done.append("5 build_ai_page.py 追加")

# ── 6. id6397 のジャンルを event に
m = re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S)
events = json.loads(m.group(1))
e = next((x for x in events if x.get("id") == 6397), None)
if not e:
    print("ABORT: id6397 が無い"); sys.exit(1)
print("id6397 %s" % e.get("name"))
print("   genre %s -> event   （_genre=%s / _piaSub=%s）" % (e.get("genre"), e.get("_genre"), e.get("_piaSub")))
e["genre"] = "event"
for f in ("_genre", "_extraGenres", "_piaSub", "_srcgenre"):
    e.pop(f, None)
new_json = json.dumps(events, ensure_ascii=False, indent=2)
h = h[:m.start(1)] + new_json.replace("\n", "\r\n") + h[m.end(1):]
done.append("6 id6397 を event に振り分け（下書きフィールドは削除）")

for d in done:
    print("  " + d)

if not APPLY:
    print("(下見のみ。--apply で書き込み)"); sys.exit(0)

shutil.copy("index.html", "index.html.bak_0904_genreevent")
shutil.copy("tools/build_ai_page.py", "tools/build_ai_page.py.bak_0904")
io.open("index.html", "w", encoding="utf-8", newline="").write(h)
io.open("tools/build_ai_page.py", "w", encoding="utf-8", newline="").write(ai)
print("WROTE index.html / tools/build_ai_page.py")
