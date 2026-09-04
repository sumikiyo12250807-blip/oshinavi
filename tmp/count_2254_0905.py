# -*- coding: utf-8 -*-
"""id2254 杉山清貴の「本当の枠数」をぴあ実ページから数え直す（2026-09-05）。

なぜ数えられなかったか＝`build_pia_entries` の券種名が潰れて、既存と同じ文言になるため
`merge_apply` が「既にある」と判定して足さない（[[feedback_pia_parser_flattens_slots]]）。

だから**ビルダーを通さずに数える**:
  ① 受付中の枠 … `ticketInformation.do?rlsCd=/lotRlsCd=` のユニーク数
  ② 発売前の枠 … リンクを持たないので、生HTMLの「販売スケジュールの行」を数える
     （[[feedback_pia_parser_flattens_slots]] の2026-09-03項＝コード数え方の穴）

出力は tmp/count_2254_0905.txt（端末の cp932 で化けるのでファイルに書く）。
"""
import json, io, re, sys, time, html as H, http.client

TARGET = int(sys.argv[1]) if len(sys.argv) > 1 else 2254
OUT = 'tmp/count_%d_0905.txt' % TARGET


def strip(s):
    return H.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s or ''))).strip()


def fetch(url):
    path = url.split('t.pia.jp', 1)[1]
    conn = http.client.HTTPSConnection('t.pia.jp', timeout=40)
    conn.request('GET', path, headers={'User-Agent': 'Mozilla/5.0', 'Accept-Encoding': 'identity'})
    raw = conn.getresponse().read().decode('utf-8', 'replace')
    conn.close()
    return raw


hh = io.open('index.html', encoding='utf-8', newline='').read()
db = {e['id']: e for e in json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);', hh, re.S).group(1))}
e = db[TARGET]

urls, seen = [], set()
for u in [(e.get('links') or {}).get('pia')] + [t.get('url') for t in e['tickets']]:
    if u and 't.pia.jp' in u and u not in seen:
        seen.add(u)
        urls.append(u)

out = io.open(OUT, 'w', encoding='utf-8')
out.write('■ id%d %s ／ %s\n' % (TARGET, e.get('artist'), e.get('name')))
out.write('  登録の枠 %d本 ／ ぴあURL %d本\n\n' % (len(e['tickets']), len(urls)))

out.write('--- 登録されている枠 ---\n')
for i, t in enumerate(e['tickets']):
    out.write('  t%-2d %s ｜ 締切%s ｜ 発売%s ｜ %s\n'
              % (i, t.get('type'), t.get('date'), t.get('startDate') or '-', t.get('url') or '(なし)'))

codes, rows = set(), []
out.write('\n--- ぴあ実ページ ---\n')
for u in urls:
    try:
        raw = fetch(u)
    except Exception as ex:
        out.write('  🚨 取得できなかった %s: %s\n' % (u, ex))
        continue
    if '大変混み合' in raw:
        out.write('  🚨 混雑ページ（sorry）に飛ばされた %s\n' % u)
        continue
    cs = set(re.findall(r'ticketInformation\.do\?(?:lot)?[Rr]lsCd=(\d+)', raw))
    codes |= cs
    marks = ['発売前', '受付中', '販売期間中', '予定枚数終了', '抽選受付終了', '販売終了', 'まもなく抽選受付']
    blocks = re.split(r'(?i)(?=<li\b|<dl\b|<tr\b|<div class="[^"]*(?:ticket|release|schedule)[^"]*")', raw)
    local, lseen = [], set()
    for b in blocks:
        t = strip(b)
        if not t or len(t) > 400 or t in lseen:
            continue
        if not any(m in t for m in marks):
            continue
        lseen.add(t)
        local.append(t)
    rows.extend(local)
    out.write('\n  %s\n    売り場コード %d個 %s\n    販売スケジュール行 %d件\n'
              % (u, len(cs), sorted(cs), len(local)))
    for t in local:
        out.write('      - %s\n' % t[:200])
    time.sleep(2.5)

out.write('\n=== まとめ ===\n')
out.write('  登録の枠            %d本\n' % len(e['tickets']))
out.write('  売り場コードのユニーク数 %d個（受付中の枠しか数えられない）\n' % len(codes))
out.write('  販売スケジュール行の延べ %d件\n' % len(rows))
out.close()
print('WROTE %s codes=%d rows=%d tickets=%d urls=%d'
      % (OUT, len(codes), len(rows), len(e['tickets']), len(urls)))
