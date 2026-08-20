# -*- coding: utf-8 -*-
"""8/20朝の削除候補（公演終了組）の素性を UTF-8 ファイルに書き出す。"""
import re, io, json

IDS = [569, 1251, 1311, 2003, 2561, 2585, 2993, 3113, 3144, 3334, 3350]
h = io.open('index.html', encoding='utf-8').read()
d = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
out = []
for e in d:
    if e['id'] in IDS:
        out.append("## id%s %s" % (e['id'], e.get('artist')))
        out.append("   title: %s" % e.get('title'))
        out.append("   venue: %s / date: %s / pref: %s / genre: %s" % (
            e.get('venue'), e.get('date'), e.get('prefecture'), e.get('genre')))
        for k, v in (e.get('links') or {}).items():
            if v:
                out.append("   link.%s: %s" % (k, v))
        for t in e.get('tickets') or []:
            out.append("   - %s | date=%s | start=%s | soldout=%s | url=%s" % (
                t.get('type'), t.get('date'), t.get('startDate'), t.get('soldout'), t.get('url') or ''))
        out.append("")
io.open('tmp/delcand_0820.txt', 'w', encoding='utf-8').write("\n".join(out))
print("ok", len(out))
