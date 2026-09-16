# -*- coding: utf-8 -*-
"""組み立てた新着（built）を「既存に畳む」「新規で入れる」「人が見る」に仕分ける（読むだけ・2026-09-15）。
split_built_0914.py の出力名違い。

  ・既存と正規化名が完全一致 1件 → 畳む（merge_with_urls_0912.py に渡す cands に target を付ける）
  ・完全一致が2件以上        → 人が見る（どこに畳むか決まらない）
  ・完全一致なし＋部分一致あり → 人が見る（「新日本フィル」⊃「日本フィル」の罠＝project_pia_presale_caught_up）
  ・どれも無い               → 新規

🚨部分一致は「既存の名前がぴあ公演名の頭に来るか」だけを材料として並べる。機械では畳まない。
使い方: python tmp/split_built_0916.py <built.json> <cands.json>
出力: tmp/split_built_0916.txt ／ tmp/merge_built_0916.json ／ tmp/merge_cands_0916.json ／ tmp/new_built_0916.json
"""
import io
import json
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')
built = json.load(io.open(sys.argv[1], encoding='utf-8'))
cands = {c['newid']: c for c in json.load(io.open(sys.argv[2], encoding='utf-8'))}
# 出力の名前の札（既定 0916＝今朝の音楽）。発売前など別のバッチは ps0916 のように変えて、前の記録を上書きしない
TAG = sys.argv[3] if len(sys.argv) > 3 else '0916'
src = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))


def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　・\-–—~〜"\'`()（）【】「」『』\[\]!！?？。、,.:：/／★☆]', '', s).lower()


idx = {}
for e in ev:
    for f in ('artist', 'name'):
        v = norm(e.get(f))
        if v:
            idx.setdefault(v, set()).add(e['id'])
by = {e['id']: e for e in ev}

merge_b, merge_c, new_b, lines = [], [], [], []
for b in built:
    a = norm(b.get('artist'))
    exact = sorted(idx.get(a, set()))
    loose = sorted({i for k, ids in idx.items() if len(k) >= 4 and len(a) >= 4 and k != a
                    and (a.startswith(k) or k.startswith(a)) for i in ids})
    tag = ' '.join('%s' % t.get('type') for t in (b.get('tickets') or [])[:2])
    if len(exact) == 1:
        c = dict(cands[b['id']])
        c['target'] = exact[0]
        merge_b.append(b)
        merge_c.append(c)
        lines.append('畳む   new%-6s → id%-5s %s ｜ %s' % (b['id'], exact[0], b.get('artist')[:30], tag[:80]))
    elif len(exact) > 1:
        lines.append('👀複数 new%-6s → %s %s ｜ %s' % (b['id'], exact, b.get('artist')[:30], tag[:80]))
    elif loose:
        lines.append('👀部分 new%-6s ～ %s %s ｜ 既存: %s' % (
            b['id'], loose[:4], b.get('artist')[:30], ' ／ '.join((by[i].get('artist') or '')[:20] for i in loose[:4])))
        new_b.append(b)  # 既定は新規。人が見て畳むと決めたら外す
    else:
        lines.append('新規   new%-6s %s ｜ %s' % (b['id'], b.get('artist')[:30], tag[:80]))
        new_b.append(b)

json.dump(merge_b, io.open('tmp/merge_built_%s.json' % TAG, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(merge_c, io.open('tmp/merge_cands_%s.json' % TAG, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(new_b, io.open('tmp/new_built_%s.json' % TAG, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
head = '組み立て %d件 ＝ 畳む %d件 / 新規（部分一致の要確認を含む）%d件 / 複数一致 %d件' % (
    len(built), len(merge_b), len(new_b), sum(1 for l in lines if l.startswith('👀複数')))
io.open('tmp/split_built_%s.txt' % TAG, 'w', encoding='utf-8').write(head + '\n' + '\n'.join(lines) + '\n')
print(head)
print('\n'.join(lines))
