# -*- coding: utf-8 -*-
"""audit_dedup.txt の「本当の抜け」24行 → build_pia_entries 用の候補JSON（1候補＝1URL）。"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
txt = io.open('tmp/x0921/audit_dedup.txt', encoding='utf-8').read()
sec = txt.split('## 本当の抜け', 1)[1].split('\n## ', 1)[0]
out = []
for i, line in enumerate(l for l in sec.splitlines() if l.startswith('- [')):
    parts = [p.strip() for p in line.split('｜')]
    name = re.sub(r'^- \[[^\]]*\]\s*', '', parts[0])
    url = parts[-1]
    out.append({'newid': 950000 + i, 'artist': name, 'urls': [url]})
json.dump(out, io.open('tmp/x0921/audit_fill_cands.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(out))
for c in out:
    print(c['newid'], c['artist'][:40], c['urls'][0])
