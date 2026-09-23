# -*- coding: utf-8 -*-
"""9/20 夜の追加収集（ぴあ 03スポーツ/04映画/05アート/06イベント）の新候補を整える。

🚨重複は URL 文字列でなく **eventCd / eventBundleCd** で見る
   （ぴあは ticket.pia.jp と t.pia.jp の2形があり、文字列比較だとすり抜ける＝朝に踏んだ）。
🚨同名の既存エントリがあるものは自動で畳まず、足し込み候補として別立てにする
   （[[feedback_check_duplicates]]／[[feedback_tour_individual_url_dup]]）。
出力: tmp/x0920/cands2_new.json（新規）／tmp/x0920/cands2_merge.json（足し込み・先が1件に決まる分）
      tmp/x0920/cands2_amb.txt（足し込み先が複数＝人が見る）
"""
import io, json, re, sys, unicodedata
sys.stdout.reconfigure(encoding='utf-8')

h = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
maxid = max(e['id'] for e in EVENTS)
codes = set(re.findall(r'event(?:Bundle)?Cd=([a-zA-Z0-9]+)', h))


def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　\[\]［］（）()【】「」｜|/・,、.]+', '', s).lower()


by = {}
for e in EVENTS:
    by.setdefault(norm(e.get('artist') or e.get('name')), []).append(e)

rows = []
for lg in ('03', '04', '05', '06'):
    try:
        rows += json.load(io.open('tmp/x0920/presale_%s.json' % lg, encoding='utf-8')).get('new') or []
    except Exception as ex:
        print('読めない lg=%s (%s)' % (lg, ex))

new, merge, amb, seen = [], [], [], set()
nid = maxid
for r in rows:
    u = r['url']
    c = re.search(r'event(?:Bundle)?Cd=([a-zA-Z0-9]+)', u)
    c = c.group(1) if c else u
    if c in seen or c in codes:
        continue
    seen.add(c)
    hit = by.get(norm(r['artist']))
    if not hit:
        nid += 1
        new.append({'newid': nid, 'artist': r['artist'], 'urls': [u]})
    elif len(hit) == 1:
        merge.append({'newid': hit[0]['id'], 'artist': r['artist'], 'urls': [u]})
    else:
        amb.append('%s | 候補id%s | %s' % (r['artist'], [e['id'] for e in hit], u))

io.open('tmp/x0920/cands2_new.json', 'w', encoding='utf-8').write(json.dumps(new, ensure_ascii=False))
io.open('tmp/x0920/cands2_merge.json', 'w', encoding='utf-8').write(json.dumps(merge, ensure_ascii=False))
io.open('tmp/x0920/cands2_amb.txt', 'w', encoding='utf-8').write('\n'.join(amb))
print('新規 %d件（id %d〜）／足し込み %d件／⚠️先が複数 %d件'
      % (len(new), maxid + 1, len(merge), len(amb)))
