# -*- coding: utf-8 -*-
"""削除候補237件を「削除は誤りという前提で」独立に再導出する（読むだけ・2026-09-20）。

候補リストを見ずに index.html からゼロから作り直し、次を機械で洗う:
  A. 公演日(date)が本当に過去か／dateLabel・type に未来の公演日が書かれていないか
  B. 配信・アーカイブ・ムビチケなど「公演後も買える」形の枠が混ざっていないか
  C. 締切(ticket.date)が未来の枠が1つでも残っていないか
  D. saleEndUnknown を持っていないか（DELETE_GATE 3章の除外リスト）
出力: tmp/x0920/verify_del.md
"""
import datetime, io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()

STREAM = re.compile(r'配信|アーカイブ|ムビチケ|オンライン|見逃し|視聴')
DATE_RE = re.compile(r'(\d{1,2})/(\d{1,2})')

h = io.open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
events = json.loads(m.group(2))
cand = set(int(x) for x in io.open('tmp/x0920/del_ids.txt', encoding='utf-8').read().split(',') if x)

flags = {'A_未来の公演日が本文に': [], 'B_配信系の枠あり': [],
         'C_締切が未来の枠あり': [], 'D_saleEndUnknown': []}
ok = 0
for e in events:
    if e['id'] not in cand:
        continue
    bad = False
    ts = e.get('tickets') or []
    # A: type / dateLabel に書かれた M/D が未来か（年跨ぎは翌年として見る）
    y = int(TODAY[:4])
    blob = ' '.join([e.get('dateLabel') or ''] + [t.get('type') or '' for t in ts])
    # 「〜9/19」のような締切表記は除く。公演日らしい「（東京 10/5公演）」形だけ見る
    for mm in re.finditer(r'[（(][^（()）]*?(\d{1,2})/(\d{1,2})[^（()）]*?公演', blob):
        mo, dd = int(mm.group(1)), int(mm.group(2))
        iso = '%04d-%02d-%02d' % (y, mo, dd)
        if iso >= TODAY:
            flags['A_未来の公演日が本文に'].append((e['id'], e.get('artist'), iso, mm.group(0)[:40]))
            bad = True
            break
    for t in ts:
        if STREAM.search((t.get('type') or '')) and not t.get('soldout') and not t.get('saleEnded'):
            flags['B_配信系の枠あり'].append((e['id'], e.get('artist'), t.get('type'), t.get('date')))
            bad = True
        if (t.get('date') or '') >= TODAY and not t.get('soldout') and not t.get('saleEnded'):
            flags['C_締切が未来の枠あり'].append((e['id'], e.get('artist'), t.get('type'), t.get('date')))
            bad = True
        if t.get('saleEndUnknown'):
            flags['D_saleEndUnknown'].append((e['id'], e.get('artist'), t.get('type')))
            bad = True
    if not bad:
        ok += 1

with io.open('tmp/x0920/verify_del.md', 'w', encoding='utf-8') as f:
    f.write('# 削除候補 %d件の独立再導出（%s）\n\n疑義なし %d件\n' % (len(cand), TODAY, ok))
    for k, rows in flags.items():
        f.write('\n## %s … %d件\n\n' % (k, len(rows)))
        for r in rows[:80]:
            f.write('- %s\n' % (r,))
print('cand=%d ok=%d' % (len(cand), ok),
      {k: len(v) for k, v in flags.items()})
