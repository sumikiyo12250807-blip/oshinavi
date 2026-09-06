# -*- coding: utf-8 -*-
"""id=6983「TALK&LIVE ザ・ゴールデンステージ <第13回>五木ひろし」から、
別公演である <第12回>新世代 ファイブスター スペシャル（9/30公演）の枠を外す。

e+の実ページで確認した中身：
  P0030007P021001 = <第12回>新世代 ファイブスター スペシャル / 9/30公演 / 〜9/29 18:00
  P0030008P021001 = <第13回>五木ひろし               / 10/31公演 / 〜10/30 18:00
エントリ名は「第13回 五木ひろし」なので、9/30枠は別エントリに分ける（第12回は別途投入）。

🚨 行ベースのピンポイント置換で書く（json.dumps で配列を作り直さない
   ＝feedback_index_html_crlf_preserve の2026-08-31項）。読み書きとも newline=''。
"""
import io, re, json

PATH = "index.html"
OLD_LINK = "https://eplus.jp/sf/detail/4370560001-P0030007P021001"
NEW_LINK = "https://eplus.jp/sf/detail/4370560001-P0030008P021001"

src = io.open(PATH, encoding="utf-8", newline="").read()
lines = src.split("\r\n")

# --- id=6983 のエントリの行範囲を特定する ---
start = end = None
for i, ln in enumerate(lines):
    if ln.strip() == '"id": 6983,':
        # エントリの開始は直前の "{" 行
        j = i
        while j >= 0 and lines[j].strip() != "{":
            j -= 1
        start = j
        # 同じ深さの "}" まで
        depth = 0
        k = start
        while k < len(lines):
            depth += lines[k].count("{") - lines[k].count("}")
            if depth == 0 and k > start:
                end = k
                break
            k += 1
        break

assert start is not None and end is not None, "id=6983 のエントリが見つからない"
block = lines[start:end + 1]
print("エントリ行範囲: %d〜%d (%d行)" % (start, end, len(block)))

# --- ① links.eplus を第13回のURLへ差し替える ---
n_link = 0
for i in range(start, end + 1):
    if '"eplus":' in lines[i] and OLD_LINK in lines[i]:
        lines[i] = lines[i].replace(OLD_LINK, NEW_LINK)
        n_link += 1
assert n_link == 1, "links.eplus の行が %d 個（1個のはず）" % n_link

# --- ② tickets のうち「長崎県 9/30公演」の枠ブロックを消す ---
t_start = None
for i in range(start, end + 1):
    if '"type": "先着一般発売（長崎県 9/30公演）〜9/29 18:00"' in lines[i]:
        # この券種を含む { … } を探す
        j = i
        while j >= start and lines[j].strip() != "{":
            j -= 1
        t_start = j
        depth = 0
        k = t_start
        while k <= end:
            depth += lines[k].count("{") - lines[k].count("}")
            if depth == 0 and k > t_start:
                t_end = k
                break
            k += 1
        break

assert t_start is not None, "9/30公演の枠が見つからない"
# 消す範囲は t_start〜t_end。直後の要素があるので、この要素の末尾の "}," ごと落とす
print("消す枠の行範囲: %d〜%d" % (t_start, t_end))
for x in range(t_start, t_end + 1):
    print("   |%s" % lines[x])

del lines[t_start:t_end + 1]

out = "\r\n".join(lines)
io.open("index.html.bak_0907_6983", "w", encoding="utf-8", newline="").write(src)
io.open(PATH, "w", encoding="utf-8", newline="").write(out)

# --- 検算：json.loads して狙った形になっているか数える ---
h = io.open(PATH, encoding="utf-8", newline="").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S).group(1))
e = [x for x in EV if x["id"] == 6983][0]
print("--- 検算 ---")
print("枠数: %d" % len(e["tickets"]))
for t in e["tickets"]:
    print("  %s | %s" % (t["type"], t.get("url")))
print("links.eplus: %s" % e["links"]["eplus"])
print("CRLF=%d bareLF=%d" % (h.count("\r\n"), len(re.findall(r"(?<!\r)\n", h))))
