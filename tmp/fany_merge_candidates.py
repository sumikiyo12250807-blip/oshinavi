# -*- coding: utf-8 -*-
"""FANYの「既存と一致」85件に対して、**足し込み先の既存エントリid**を機械で特定する。
（同じ公演がぴあ等で登録済み＝FANYの売り場リンクを足すと「買える場所」が増える）

  python tmp/fany_merge_candidates.py            … 候補表だけ
  python tmp/fany_merge_candidates.py --apply    … links.fany を足す

決め方（推測しない）＝名前(artist/name)の正規化 × 公演日 × 会場の正規化 が**全部一致**した1件だけ。
2件以上に当たったもの・1件も当たらないものは**触らずに報告**（人が見る）。
"""
import io, json, re, sys, unicodedata

APPLY = '--apply' in sys.argv
PATH = 'index.html'


def norm(s):
    s = unicodedata.normalize('NFKC', s or '').lower()
    return re.sub(r'[\s　・･,，.。!！?？~〜\-—–_/／\(\)（）\[\]【】「」『』"\'’]', '', s)


built = json.load(open('tmp/built_fany_0921.json', encoding='utf-8'))
h = io.open(PATH, encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
have = set(re.findall(r'ticket\.fany\.lol/event/detail/(\d+)', h))

idx = {}
for e in EVENTS:
    blob = json.dumps(e, ensure_ascii=False)
    days = set(re.findall(r'\d{4}-\d{2}-\d{2}', blob))
    nv = norm(e.get('venue'))
    for n in {norm(e.get('artist')), norm(e.get('name'))}:
        if not n:
            continue
        for d in days:
            idx.setdefault((n, d, nv), set()).add(e['id'])

by_id = {e['id']: e for e in EVENTS}
one, many, none = [], [], []
for e in built:
    fid = re.search(r'/event/detail/(\d+)', e['links'].get('fany') or '')
    if not fid or fid.group(1) in have:
        continue                      # 投入済み（＝新規で入った分）は対象外
    na, nn, nv = norm(e.get('artist')), norm(e.get('name')), norm(e.get('venue'))
    hits = set(idx.get((na, e['date'], nv)) or set()) | set(idx.get((nn, e['date'], nv)) or set())
    if len(hits) == 1:
        one.append((e, list(hits)[0]))
    elif hits:
        many.append((e, sorted(hits)))
    else:
        none.append(e)

out = io.open('tmp/fany_merge_candidates.txt', 'w', encoding='utf-8')
out.write('FANYで入れなかった分 %d件 → 足し込み先が1つ %d / 2つ以上 %d / 見つからない %d\n\n'
          % (len(one) + len(many) + len(none), len(one), len(many), len(none)))
out.write('=== 足し込み先が1つに決まった（links.fany を足す）===\n')
for e, i in sorted(one, key=lambda x: x[1]):
    ex = by_id[i]
    out.write('id%-6s %-34s %s @ %s\n' % (i, (ex.get('artist') or '')[:34], ex.get('date'),
                                          (ex.get('venue') or '')[:20]))
    out.write('        FANY: %-30s %s / 枠%d\n'
              % (e['name'][:30], e['links']['fany'], len(e['tickets'])))
    out.write('        いまのリンク: %s\n'
              % {k: v for k, v in (ex.get('links') or {}).items() if v})
out.write('\n=== 足し込み先が2つ以上（触らない）===\n')
for e, ids in many:
    out.write('  %s / %s / %s → id%s\n' % (e['name'][:34], e['venue'][:18], e['date'], ids))
out.write('\n=== 見つからない（会場の書き方が違うだけの可能性）===\n')
for e in none:
    out.write('  %s / %s / %s\n    %s\n'
              % (e['name'][:34], e['venue'][:22], e['date'], e['links']['fany']))
out.close()
print('wrote tmp/fany_merge_candidates.txt  one=%d many=%d none=%d' % (len(one), len(many), len(none)))

if APPLY and one:
    n = 0
    for e, i in one:
        ex = by_id[i]
        ls = ex.setdefault('links', {})
        if not ls.get('fany'):
            ls['fany'] = e['links']['fany']
            n += 1
    new = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
    io.open('index.html.bak_0921_fanymerge', 'w', encoding='utf-8', newline='').write(h)
    io.open(PATH, 'w', encoding='utf-8', newline='').write(
        h[:m.start()] + m.group(1) + new + m.group(3) + h[m.end():])
    raw = open(PATH, 'rb').read()
    print('links.fany を足した %d件 / CRCRLF %d / 素のLF %d'
          % (n, raw.count(b'\r\r\n'), len(re.findall(rb'(?<!\r)\n', raw))))
