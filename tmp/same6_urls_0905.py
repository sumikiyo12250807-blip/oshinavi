# -*- coding: utf-8 -*-
"""「公演が全部載っている」6件の既存枠が、どの売り場のURLを持っているか見る。

飛び先が同じ（e+の同じ-Pページ）なら、候補の枠は同じものなので足さない。
飛び先が違う（ぴあ等）なら、[[feedback_dedup_badges_keeps_urls]] に従って両方残すか検討する。
"""
import json, io, re

SAME = {6960: 1477, 6965: 2325, 6976: 4240, 6981: 5784, 6984: 5762, 6987: 5766,
        6958: 5879, 6980: 5251, 6989: 3892, 6994: 579}

hh = io.open('index.html', encoding='utf-8', newline='').read()
db = {e['id']: e for e in json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);', hh, re.S).group(1))}
built = {b['id']: b for b in json.load(io.open('tmp/eplus_batch2_0905.json', encoding='utf-8'))}

out = io.open('tmp/same6_urls_0905.txt', 'w', encoding='utf-8')
for cid, tid in SAME.items():
    e, b = db[tid], built[cid]
    cu = {t.get('url') for t in b['tickets']}
    eu = [t.get('url') for t in (e.get('tickets') or [])]
    def kind(u):
        if not u:
            return 'なし'
        if 'eplus' in u:
            return 'e+'
        if 'pia' in u:
            return 'ぴあ'
        return 'その他'
    out.write('■ 既存id%d %s ｜ 既存枠%d本 %s\n' % (tid, e.get('artist'), len(eu),
                                                dict((k, [kind(u) for u in eu].count(k))
                                                     for k in set(kind(u) for u in eu))))
    same_url = sum(1 for u in eu if u in cu)
    out.write('   候補と同じURLを持つ既存枠 %d本 / 候補の枠 %d本\n\n' % (same_url, len(b['tickets'])))
out.close()
print('OK')
