# -*- coding: utf-8 -*-
"""今日振り分けた分のうち「別エージェントのチェックを通したのはどれか」を機械で数える。
記憶や自分の発言でなく、実ファイルから出す。"""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

# エージェントに独立判定させた78件（渡したリスト）
agent_seen = set()
for line in open("tmp/agent_genres_0826.txt", encoding="utf-8"):
    p = line.split()
    if len(p) == 2:
        agent_seen.add(int(p[0]))

# そのうち、あたしの下書きと一致して適用した72件
agreed = set(json.load(open("tmp/assign_ok_0826.json", encoding="utf-8")))

# ユーザーが直接ジャンルを決めた3件
by_user = {5098, 5119, 5120}

# 振り分け前（115件）のプール ＝ 8/26 の作業開始時点
before = json.load(open("tmp/assign_ids_0826.json", encoding="utf-8"))  # 78件の対象id
src = open("index.html", encoding="utf-8").read()
m = re.search(r"const EVENTS = (\[.*?\]);\n", src, re.S)
now_new = {e["id"] for e in json.loads(m.group(1)) if e.get("genre") == "new"}

# 今日振り分けたid＝「115件のプールにいて、今はnewでない」もの
pool115 = json.load(open("tmp/exclude_0826.json", encoding="utf-8")) if False else None
# exclude_0826.txt は「振り分けなかった43件」なので、それとassign_okを足すと115件
excluded43 = {int(x) for x in open("tmp/exclude_0826.txt", encoding="utf-8").read().split(",")}
pool115 = agreed | excluded43
assigned_today = pool115 - now_new

a_agreed = assigned_today & agreed
a_user = assigned_today & by_user
a_seen_not_agreed = (assigned_today & agent_seen) - agreed
a_unseen = assigned_today - agent_seen - by_user

print("=== 今日振り分けた %d件の内訳 ===" % len(assigned_today))
print("  ✅エージェントが判定し、あたしと一致した      %d件" % len(a_agreed))
print("  ⚠️エージェントは見たが、判定が割れた/迷った   %d件 → %s" % (
    len(a_seen_not_agreed), sorted(a_seen_not_agreed)))
print("  👤ユーザーが直接ジャンルを指定した            %d件 → %s" % (len(a_user), sorted(a_user)))
print("  🚨エージェントに一度も見せていない            %d件 → %s" % (len(a_unseen), sorted(a_unseen)))
