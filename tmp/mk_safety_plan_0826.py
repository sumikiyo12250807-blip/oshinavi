# -*- coding: utf-8 -*-
"""ヒールの安全弁が止めた9件を、追加URLなしで再導出するplanを作る。
（そのエントリが既に持っている links.pia ＋ 全 ticket.url だけを使う）"""
import json

IDS = [1, 177, 516, 571, 761, 1095, 1098, 3118, 3926]
plan = {str(i): [] for i in IDS}
json.dump(plan, open("tmp/safety_plan_0826.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("%d件 → tmp/safety_plan_0826.json" % len(plan))
