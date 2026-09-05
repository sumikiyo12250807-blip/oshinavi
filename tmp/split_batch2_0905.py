# -*- coding: utf-8 -*-
"""batch2 を「新規で入れる分」と「既存ツアーへ足す分」に分ける（2026-09-05）。

dup3_0905.py の判定に従う:
  同じ(6件)  … 公演が全部すでに載っている → 何もしない
  別(39件)   … 新規エントリとして投入
  保留(4件)  … 同じアーティストのツアーが既にある。**新規で作らず、
                既存エントリに「まだ載っていない公演の枠」だけ足す**
                （[[feedback_tour_consolidate]]＝ツアーは1エントリ。
                  足すだけなので既存の枠は触らない＝飛び先の破壊が起きない）

出力:
  tmp/batch2_new_0905.json    … inject_built.py に渡す新規エントリ
  tmp/batch2_merge_0905.json  … {既存id: [足す枠...]} と会場の追記
"""
import json, io, re, unicodedata

PREF = ('北海道|青森|岩手|宮城|秋田|山形|福島|茨城|栃木|群馬|埼玉|千葉|東京|神奈川|新潟|富山|石川|福井|'
        '山梨|長野|岐阜|静岡|愛知|三重|滋賀|京都|大阪|兵庫|奈良|和歌山|鳥取|島根|岡山|広島|山口|徳島|香川|'
        '愛媛|高知|福岡|佐賀|長崎|熊本|大分|宮崎|鹿児島|沖縄')
PREF_SET = set(PREF.split('|'))
RE_SLOT = re.compile(r'[（(]\s*((?:%s)(?:都|府|県)?)[^）)]*?(\d{1,2})/(\d{1,2})' % PREF)

SAME = [6960, 6965, 6976, 6981, 6984, 6987]
MERGE = {6958: 5879, 6980: 5251, 6989: 3892, 6994: 579}


def key(t):
    out = set()
    for m in RE_SLOT.finditer(t.get('type') or ''):
        p = m.group(1)
        if p not in PREF_SET:
            p = re.sub(r'[都府県]$', '', p)
        out.add((p, int(m.group(2)), int(m.group(3))))
    return out


hh = io.open('index.html', encoding='utf-8', newline='').read()
db = {e['id']: e for e in json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);', hh, re.S).group(1))}
maxid = max(db)

built = {b['id']: b for b in json.load(io.open('tmp/eplus_batch2_0905.json', encoding='utf-8'))}

# --- 新規 ---------------------------------------------------------------
new, nid = [], maxid + 1
for i in sorted(built):
    if i in SAME or i in MERGE:
        continue
    b = built[i]
    b['id'] = nid
    nid += 1
    new.append(b)
json.dump(new, io.open('tmp/batch2_new_0905.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# --- 既存へ足す ---------------------------------------------------------
merge = {}
rep = io.open('tmp/batch2_merge_0905.txt', 'w', encoding='utf-8')
for cid, tid in MERGE.items():
    b, e = built[cid], db[tid]
    have = set()
    for t in (e.get('tickets') or []):
        have |= key(t)
    add = [t for t in b['tickets'] if key(t) and not (key(t) & have)]
    merge[str(tid)] = add
    rep.write('■ 既存 id%d %s ／ %s\n' % (tid, e.get('artist'), e.get('name')))
    rep.write('   既に載っている公演 %s\n' % sorted(have))
    rep.write('   足す枠 %d本:\n' % len(add))
    for t in add:
        rep.write('     - %s ｜ 締切%s ｜ %s\n' % (t['type'], t['date'], t.get('url', '')))
    rep.write('\n')
rep.write('足す先 %d エントリ / 足す枠 合計 %d本\n'
          % (len(merge), sum(len(v) for v in merge.values())))
rep.close()
json.dump(merge, io.open('tmp/batch2_merge_0905.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

print('NEW=%d (id%d..%d) MERGE_ENTRIES=%d MERGE_SLOTS=%d SKIP_SAME=%d'
      % (len(new), new[0]['id'], new[-1]['id'], len(merge),
         sum(len(v) for v in merge.values()), len(SAME)))
