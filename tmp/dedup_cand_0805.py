# -*- coding: utf-8 -*-
"""候補JSON（harvest_new出力）と既存index.htmlの重複チェック。
  ①eventCd/eventBundleCd 一致＝確実な重複
  ②NFKC正規化したアーティスト名の完全一致／包含
  ③候補どうしの重複（同じeventCdが2行）
使い方: python tmp/dedup_cand_0805.py tmp/cand_0805.json
"""
import json, re, sys, unicodedata

sys.stdout.reconfigure(encoding='utf-8')
cand = json.load(open(sys.argv[1], encoding='utf-8'))
h = open('index.html', encoding='utf-8').read()
E = json.loads(re.search(r'const\s+EVENTS\s*=\s*(\[.*?\]);\s*\n', h, re.S).group(1))

CD = re.compile(r'event(?:Bundle)?Cd=([A-Za-z0-9]+)')


def codes_of_entry(e):
    s = set()
    for u in [(e.get('links') or {}).get('pia') or ''] + [t.get('url') or '' for t in (e.get('tickets') or [])]:
        s |= set(CD.findall(u))
    return s


def norm(s):
    s = unicodedata.normalize('NFKC', s or '').lower()
    return re.sub(r'[\s　・,，.。/／\-–—~〜～!！?？&＆\'"’”（）()\[\]【】]', '', s)


ex_codes = {}
ex_names = {}
for e in E:
    for c in codes_of_entry(e):
        ex_codes.setdefault(c, []).append(e)
    ex_names.setdefault(norm(e.get('artist') or ''), []).append(e)

seen_code = {}
hits = 0
for c in cand:
    cc = set()
    for u in c.get('urls') or []:
        cc |= set(CD.findall(u))
    nm = norm(c.get('artist') or '')
    msgs = []
    for x in cc:
        if x in ex_codes:
            for e in ex_codes[x]:
                msgs.append('🚨eventCd一致 id=%d %s' % (e['id'], e.get('artist')))
        if x in seen_code:
            msgs.append('🚨候補内で重複 newid=%d' % seen_code[x])
        seen_code[x] = c['newid']
    for e in ex_names.get(nm, []):
        msgs.append('⚠️名前完全一致 id=%d %s' % (e['id'], e.get('artist')))
    if not msgs and len(nm) >= 5:
        for k, v in ex_names.items():
            if len(k) >= 5 and (nm in k or k in nm):
                msgs.append('⚠️名前包含 id=%d %s' % (v[0]['id'], v[0].get('artist')))
                break
    if msgs:
        hits += 1
        print('newid=%d %s' % (c['newid'], c.get('artist')))
        for m in dict.fromkeys(msgs):
            print('    ' + m)

print('=== 候補%d件 / 要確認 %d件 ===' % (len(cand), hits))
