# -*- coding: utf-8 -*-
"""7/31セッションのログを機械で調べる：X主役選定で外部データを取りに行ったか。"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SID = "8b1f6d1b-939a-4c6a-bb35-3db3ed4e98fd"
PATH = r"C:\Users\user\.claude\projects\C--Users-user-oshinavi\%s.jsonl" % SID

tools = {}
websearch_queries = []
webfetch_urls = []
kw_hits = {k: 0 for k in ["フォロワー", "follower", "インプレッション", "表示回数",
                          "リポスト", "いいね", "キャパ", "座席数", "動員"]}
lines = 0

with open(PATH, "rb") as f:
    for raw in f:
        lines += 1
        try:
            rec = json.loads(raw.decode("utf-8", "replace"))
        except Exception:
            continue
        msg = rec.get("message") or {}
        content = msg.get("content")
        blocks = content if isinstance(content, list) else []
        for b in blocks:
            if not isinstance(b, dict):
                continue
            if b.get("type") == "tool_use":
                name = b.get("name", "?")
                tools[name] = tools.get(name, 0) + 1
                inp = b.get("input") or {}
                if name == "WebSearch":
                    websearch_queries.append(str(inp.get("query", "")))
                elif name == "WebFetch":
                    webfetch_urls.append(str(inp.get("url", "")))
        blob = raw.decode("utf-8", "replace")
        for k in kw_hits:
            if k in blob:
                kw_hits[k] += 1

print("ログ行数: %d" % lines)
print("\n=== 使ったツールと回数 ===")
for k in sorted(tools, key=lambda x: -tools[x]):
    print("  %-22s %d" % (k, tools[k]))

print("\n=== WebSearch のクエリ全件 (%d件) ===" % len(websearch_queries))
for q in websearch_queries:
    print("  - %s" % q)

print("\n=== WebFetch のURL全件 (%d件) ===" % len(webfetch_urls))
for u in webfetch_urls:
    print("  - %s" % u)

print("\n=== 人気指標キーワードの出現行数 ===")
for k in kw_hits:
    print("  %-14s %d行" % (k, kw_hits[k]))
