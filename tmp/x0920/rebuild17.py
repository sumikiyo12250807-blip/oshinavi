# -*- coding: utf-8 -*-
"""「カードは出るのに買える枠0」なのに **ぴあには買える枠がある** 17件を取り直す（2026-09-20 朝）。

いきさつ＝`check_zero_badge` が60件を要対応で出し、`mark_soldout` にかけたら
17件が alive（ぴあに買える枠が1〜3件ある）だった＝**取り込み漏れ**。

🚨build_pia_entries に複数URLを渡すと2本目以降に ticket.url が付かない
  （[[feedback_build_pia_multiurl_loses_ticket_url]]）ので**1件ずつ**回す。
出力: tmp/x0920/rebuilt17.json（組み上がり）
"""
import io, json, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')

rows = [ln.split('\t') for ln in io.open('tmp/x0920/alive17.txt', encoding='utf-8').read().splitlines() if ln]
out = []
for n, (i, name, url) in enumerate(rows, 1):
    if not url:
        print('[%d/%d] id=%s URLが無い＝飛ばす' % (n, len(rows), i))
        continue
    cand = [{'newid': int(i), 'artist': name, 'urls': [url]}]
    io.open('tmp/x0920/_one.json', 'w', encoding='utf-8').write(json.dumps(cand, ensure_ascii=False))
    r = subprocess.run([sys.executable, 'tools/build_pia_entries.py', 'tmp/x0920/_one.json'],
                       capture_output=True)
    txt = r.stdout.decode('utf-8', errors='replace')
    j = txt.find('[')
    try:
        got = json.loads(txt[j:])
    except Exception as e:
        print('[%d/%d] id=%s 組めない（%s）' % (n, len(rows), i, e))
        continue
    for g in got:
        g['id'] = int(i)
        out.append(g)
    print('[%d/%d] id=%s %s → 枠%d' % (n, len(rows), i, name[:26],
                                       sum(len(g.get('tickets') or []) for g in got)))
io.open('tmp/x0920/rebuilt17.json', 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False))
print('\n組み上がり %d件 / 枠 %d本 → tmp/x0920/rebuilt17.json'
      % (len(out), sum(len(g.get('tickets') or []) for g in out)))
