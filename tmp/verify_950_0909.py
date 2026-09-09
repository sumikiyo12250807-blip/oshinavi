# -*- coding: utf-8 -*-
"""id=950 の eventCd=2630742 の本当の枠数(rlsCd/lotRlsCdのユニーク数)を数える。"""
import re
import io
import sys
from collections import Counter

sys.path.insert(0, r"C:\Users\user\oshinavi\tools")
from build_pia_entries import fetch   # noqa: E402

URL = "https://t.pia.jp/pia/event/event.do?eventCd=2630742"
h = fetch(URL)
rls = re.findall(r"(?:lotRlsCd|rlsCd)=([0-9A-Za-z]+)", h)
uniq = sorted(set(rls))
# 公演日ごとの出現
days = re.findall(r"(20\d\d/\d{1,2}/\d{1,2})\([^)]*\)\s*天満天神繁昌亭", re.sub(r"<[^>]+>", " ", h))
buf = []
buf.append("URL=%s  len(html)=%d" % (URL, len(h)))
buf.append("rlsCd/lotRlsCd 出現=%d ユニーク=%d" % (len(rls), len(uniq)))
buf.append("ユニーク一覧: %s" % ", ".join(uniq))
buf.append("公演日の出現: %s" % dict(Counter(days)))
io.open(r"C:\Users\user\oshinavi\tmp\verify_950_0909.txt", "w", encoding="utf-8").write("\n".join(buf) + "\n")
print("ok")
