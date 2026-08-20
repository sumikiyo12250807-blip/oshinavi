# -*- coding: utf-8 -*-
"""奥華子(id2606)の登録内容を見る＝8/10発売ぶんのX投稿を書くため。"""
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"C:\Users\user\oshinavi\tools")
from check_expired import extract_events_array  # noqa: E402

evs = {e["id"]: e for e in extract_events_array(r"C:\Users\user\oshinavi\index.html")}
for eid in (2606, 3134):
    e = evs[eid]
    print("=" * 70)
    print(json.dumps({k: v for k, v in e.items() if k != "links"}, ensure_ascii=False, indent=1))
    print("links: %s" % json.dumps(e.get("links"), ensure_ascii=False))
