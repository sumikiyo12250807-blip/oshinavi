# -*- coding: utf-8 -*-
"""今朝のセッション e0d92ce5 から、フォロワー数の実数が取れていたか抜き出す。"""
import io
import json
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PATH = r"C:\Users\user\.claude\projects\C--Users-user-oshinavi\e0d92ce5-a6bc-4f3c-82ac-1a2a5e39ea68.jsonl"

# 「フォロワー」の近くに数字がある行を拾う
pat = re.compile(r"[^\n]{0,80}フォロワー[^\n]{0,80}")
num = re.compile(r"(\d[\d,\.]*\s*(?:万|人|k|K|M)?)")

seen = set()
out = []
with open(PATH, "rb") as f:
    for raw in f:
        try:
            rec = json.loads(raw.decode("utf-8", "replace"))
        except Exception:
            continue
        role = (rec.get("message") or {}).get("role")
        content = (rec.get("message") or {}).get("content")
        blocks = content if isinstance(content, list) else []
        for b in blocks:
            if not isinstance(b, dict):
                continue
            txt = ""
            if b.get("type") == "text":
                txt = b.get("text") or ""
            elif b.get("type") == "tool_result":
                c = b.get("content")
                if isinstance(c, str):
                    txt = c
                elif isinstance(c, list):
                    txt = " ".join(x.get("text", "") for x in c if isinstance(x, dict))
            if not txt or "フォロワー" not in txt:
                continue
            for m in pat.findall(txt):
                s = " ".join(m.split())
                if not num.search(s):
                    continue
                key = s[:60]
                if key in seen:
                    continue
                seen.add(key)
                out.append((role or "?", s))

print("フォロワー＋数字を含む断片: %d件\n" % len(out))
for role, s in out:
    print("[%s] %s" % (role, s))
