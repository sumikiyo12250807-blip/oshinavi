# -*- coding: utf-8 -*-
"""同名の既存がある19件を「公演が本当に重なっているか」で切り分ける。

判定材料＝券種名に必ず入っている「（県 M/D公演）」。
これは候補側も既存側も同じ形なので、**(県, M/D) の集合の重なり**で機械的に判定できる。

  重なり = 候補の公演のうち、既存エントリにも同じ (県, M/D) がある割合
   - 100%  → 同じ公演/同じツアー ＝ 新規で入れない（既存へ枠を足す）
   - 0%    → 別の公演 ＝ 新規で入れてよい
   - 途中   → 人が見る（保留）
"""
import json, io, re, unicodedata

PREF = ('北海道|青森|岩手|宮城|秋田|山形|福島|茨城|栃木|群馬|埼玉|千葉|東京|神奈川|新潟|富山|石川|福井|'
        '山梨|長野|岐阜|静岡|愛知|三重|滋賀|京都|大阪|兵庫|奈良|和歌山|鳥取|島根|岡山|広島|山口|徳島|香川|'
        '愛媛|高知|福岡|佐賀|長崎|熊本|大分|宮崎|鹿児島|沖縄')
PREF_SET = set(PREF.split('|'))
RE_SLOT = re.compile(r'[（(]\s*((?:%s)(?:都|府|県)?)[^）)]*?(\d{1,2})/(\d{1,2})' % PREF)


def nz(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　・･／/,、]', '', s).lower()


def slots(e):
    out = set()
    for t in (e.get('tickets') or []):
        for m in RE_SLOT.finditer(t.get('type') or ''):
            pref = m.group(1)
            if pref not in PREF_SET:
                pref = re.sub(r'[都府県]$', '', pref)
            out.add((pref, int(m.group(2)), int(m.group(3))))
    return out


hh = io.open('index.html', encoding='utf-8', newline='').read()
db = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);', hh, re.S).group(1))
byname = {}
for e in db:
    byname.setdefault(nz(e.get('artist')), []).append(e)

built = json.load(io.open('tmp/eplus_batch2_0905.json', encoding='utf-8'))

same, diff, hold = [], [], []
out = io.open('tmp/dup3_0905.txt', 'w', encoding='utf-8')
for b in built:
    hit = byname.get(nz(b.get('artist')), [])
    if not hit:
        diff.append(b['id'])
        continue
    bs = slots(b)
    best, bestr = None, -1.0
    for e in hit:
        es = slots(e)
        r = (len(bs & es) / len(bs)) if bs else 0.0
        if r > bestr:
            best, bestr = e, r
    tag = '同じ' if bestr >= 0.999 else ('別' if bestr == 0 else '保留')
    (same if tag == '同じ' else (diff if tag == '別' else hold)).append(b['id'])
    out.write('%s id%d %s ／ %s\n' % (tag, b['id'], b['artist'], b['name']))
    out.write('     候補の公演 %d件 %s\n' % (len(bs), sorted(bs)))
    out.write('     いちばん近い既存 id%s（重なり %.0f%%） %s\n'
              % (best['id'], bestr * 100, sorted(slots(best))))

out.write('\n同じ(新規で入れない)=%s\n別(新規で入れる)=%d件\n保留(人が見る)=%s\n'
          % (same, len(diff), hold))
out.close()
print('SAME=%d DIFF=%d HOLD=%d' % (len(same), len(diff), len(hold)))
print('SAME_IDS=%s' % same)
print('HOLD_IDS=%s' % hold)
