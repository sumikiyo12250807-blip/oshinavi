# -*- coding: utf-8 -*-
import json, re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

d = json.load(open('tmp/presale_01_0626.json', encoding='utf-8'))
new = d['new']

def norm_url(u):
    mb = re.search(r'eventBundleCd=(\w+)', u)
    if mb:
        return 'https://t.pia.jp/pia/event/event.do?eventBundleCd=' + mb.group(1)
    me = re.search(r'eventCd=(\w+)', u)
    if me:
        return 'https://t.pia.jp/pia/event/event.do?eventCd=' + me.group(1)
    return u

# 同一アーティスト名でまとめるツアー（手動指定）
MERGE = {'ＲｅｏＮａ', '古川雄大'}

groups = []   # list of (artist, [urls])
by_name = {}
for c in new:
    art = c['artist']
    url = norm_url(c['url'])
    if art in MERGE:
        if art in by_name:
            if url not in by_name[art]:
                by_name[art].append(url)
            continue
        else:
            by_name[art] = [url]
            groups.append([art, by_name[art]])
    else:
        groups.append([art, [url]])

cands = []
nid = 1332
for art, urls in groups:
    cands.append({'newid': nid, 'artist': art, 'urls': urls})
    nid += 1

json.dump(cands, open('tmp/candidates_0626.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('候補エントリ数:', len(cands), '（newid 1332〜%d）' % (nid-1))
for c in cands:
    print(c['newid'], '|', c['artist'][:34], '| urls:', len(c['urls']))
