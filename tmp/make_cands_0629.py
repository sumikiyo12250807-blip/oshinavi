# -*- coding: utf-8 -*-
"""harvest出力(new[])→ build_pia_entries用候補 [{newid, artist, urls}]。
 ① eventCd/bundleCd 正規化＆完全重複URL除去
 ② artist文字列が完全一致する複数公演は urls をまとめて1ツアー化
    (かりゆし58の別eventCd×5 等。Kazuki Katoは tour名違いで別artist→統合されない)
 ③ 先頭N(=50)グループを採用・id 1544 から連番"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

N = int(sys.argv[1]) if len(sys.argv) > 1 else 50
START_ID = 1544

d = json.load(open('tmp/harvest_0629_music.json', encoding='utf-8'))
new = d['new']

def norm_url(u):
    m = re.search(r'eventBundleCd=(b\w+)', u)
    if m:
        return 'https://t.pia.jp/pia/event/event.do?eventBundleCd=' + m.group(1)
    m = re.search(r'eventCd=(\d+)', u)
    if m:
        return 'https://t.pia.jp/pia/event/event.do?eventCd=' + m.group(1)
    return u

# 出現順を保ったまま artist でグルーピング(urlは重複除去)
groups = {}      # artist -> {'artist':, 'urls':[...]}
order = []
for it in new:
    a = it['artist']
    u = norm_url(it['url'])
    if a not in groups:
        groups[a] = {'artist': a, 'urls': []}
        order.append(a)
    if u not in groups[a]['urls']:
        groups[a]['urls'].append(u)

picked = order[:N]
cands = []
nid = START_ID
for a in picked:
    g = groups[a]
    cands.append({'newid': nid, 'artist': g['artist'], 'urls': g['urls']})
    nid += 1

json.dump(cands, open('tmp/cands_0629.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
multi = [c for c in cands if len(c['urls']) > 1]
print('全候補グループ:', len(order), '/ 採用:', len(cands), '(ids %d..%d)' % (START_ID, nid - 1))
print('複数url(ツアー統合)グループ:', len(multi))
for c in multi:
    print('  ', c['newid'], c['artist'][:30], '=', len(c['urls']), 'url')
