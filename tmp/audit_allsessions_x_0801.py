# -*- coding: utf-8 -*-
"""全セッションログを走査：X関連の数値をどこかで取りに行った形跡を探す。"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

DIR = r"C:\Users\user\.claude\projects\C--Users-user-oshinavi"
files = sorted([f for f in os.listdir(DIR) if f.endswith(".jsonl")],
               key=lambda f: os.path.getmtime(os.path.join(DIR, f)), reverse=True)

print("セッション数: %d\n" % len(files))

for fn in files:
    path = os.path.join(DIR, fn)
    mt = os.path.getmtime(path)
    import time
    stamp = time.strftime("%m/%d %H:%M", time.localtime(mt))
    tools = {}
    xsearch = []
    xfetch = []
    chrome = []
    with open(path, "rb") as f:
        for raw in f:
            try:
                rec = json.loads(raw.decode("utf-8", "replace"))
            except Exception:
                continue
            msg = rec.get("message") or {}
            content = msg.get("content")
            if not isinstance(content, list):
                continue
            for b in content:
                if not isinstance(b, dict) or b.get("type") != "tool_use":
                    continue
                name = b.get("name", "?")
                tools[name] = tools.get(name, 0) + 1
                inp = b.get("input") or {}
                if "chrome" in name.lower():
                    chrome.append("%s %s" % (name, str(inp)[:120]))
                if name == "WebSearch":
                    q = str(inp.get("query", ""))
                    if any(k in q for k in ["フォロワー", "人気", "インプレ", "twitter", "Twitter", "X ", "いいね", "リポスト", "ランキング"]):
                        xsearch.append(q)
                if name == "WebFetch":
                    u = str(inp.get("url", ""))
                    if any(k in u for k in ["x.com", "twitter", "socialblade", "achikochi", "ranking", "twstalker"]):
                        xfetch.append(u)
    interesting = chrome or xsearch or xfetch
    mark = "★" if interesting else " "
    print("%s %s  %s  tools=%d種" % (mark, stamp, fn[:8], len(tools)))
    if chrome:
        print("    [Chrome操作] %d件" % len(chrome))
        for c in chrome[:6]:
            print("      - %s" % c)
    if xsearch:
        print("    [X関連の検索] %d件" % len(xsearch))
        for q in xsearch[:10]:
            print("      - %s" % q)
    if xfetch:
        print("    [X関連のfetch] %d件" % len(xfetch))
        for u in xfetch[:10]:
            print("      - %s" % u)
