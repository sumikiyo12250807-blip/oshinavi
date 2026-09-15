# -*- coding: utf-8 -*-
"""総ざらいの2本め（audit_posts2）が終わった後の差分を、組み立て用の候補にする（読むだけ・2026-09-15夜）。
1本めの分（tmp/x0916/cand_merge.json・cand_new.json）はもう組み立て中なので、その URL を除いた残りだけを出す。
audit_dedup の取り違え（日本フィル↔新日本フィル）で「登録済みらしい」に落ちた本当の抜けを EXTRA_URLS で足す：
  日本フィル コバケン・ワールド Vol.44 9/27（eventCd=2617957）＝id9754 佐渡裕指揮 新日本フィル に当たったが別の楽団
分け方は audit_cands.py と同じ。新規の id は1本めの最後の newid の次から。
使い方: python tmp/x0916/audit_dedup.py → python tmp/x0916/audit_cands2.py
出力: tmp/x0916/cand_merge2.json ／ tmp/x0916/cand_new2.json
"""
import io
import json
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')
EXTRA_URLS = {'https://ticket.pia.jp/pia/event.do?eventCd=2617957'}


def norm(s):
    return re.sub(r'[\s　]+', '', unicodedata.normalize('NFKC', s or '')).lower()


def parse(path):
    out, cur = [], None
    for ln in io.open(path, encoding='utf-8').read().splitlines():
        m = re.match(r'^\s+\[([^\]]*)\] (.+)$', ln)
        if m:
            cur = {'status': m.group(1), 'title': m.group(2)}
            out.append(cur)
            continue
        m = re.match(r'^\s+公演日: (.*?) ／ 会場: (.*)$', ln)
        if m and cur:
            cur['perf'], cur['venue'] = m.group(1), m.group(2)
            continue
        m = re.match(r'^\s+発売日: (.*)$', ln)
        if m and cur:
            cur['rls'] = m.group(1)
            continue
        m = re.match(r'^\s+URL\s+: (\S+)$', ln)
        if m and cur:
            cur['url'] = m.group(1)
    return out


done_m = json.load(io.open('tmp/x0916/cand_merge.json', encoding='utf-8'))
done_n = json.load(io.open('tmp/x0916/cand_new.json', encoding='utf-8'))
done = {u for c in done_m + done_n for u in c['urls']}
real = [c for c in json.load(io.open('tmp/x0916/audit_real_missing.json', encoding='utf-8')) if c['url'] not in done]
have = {c['url'] for c in real} | done
for c in parse('tmp/x0916/audit_posts2.txt'):
    if c.get('url') in EXTRA_URLS and c['url'] not in have:
        real.append(c)
        have.add(c['url'])

src = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
by_artist = {}
for e in ev:
    by_artist.setdefault(norm(e.get('artist')), []).append(e)
next_id = max([e['id'] for e in ev] + [c['newid'] for c in done_n]) + 1
tmp_id = 99101


def pref_of(venue):
    m = re.search(r'\(([^()]*?[都道府県])\)\s*$', unicodedata.normalize('NFKC', venue or ''))
    return m.group(1) if m else ''


new, merge = [], []
for c in real:
    rls = c.get('rls') or ''
    rls = '' if rls.startswith('(空') else rls
    base = {'artist': c['title'], 'urls': [c['url']], '_lg': '', '_perfdate': c.get('perf') or '',
            '_rlsdate': rls, '_pref': pref_of(c.get('venue'))}
    hits = by_artist.get(norm(c['title']), [])
    if len(hits) == 1:
        d = dict(base, newid=tmp_id, target=hits[0]['id'])
        tmp_id += 1
        merge.append(d)
        print('足し込み id%-5s ← %s ｜%s' % (hits[0]['id'], c['title'][:36], c.get('perf')))
    else:
        d = dict(base, newid=next_id)
        next_id += 1
        new.append(d)
        print('新規     id%-5s   %s ｜%s%s' % (d['newid'], c['title'][:36], c.get('perf'),
                                           '（同じ名前のエントリ %d本＝足し先が決まらない）' % len(hits) if hits else ''))
io.open('tmp/x0916/cand_merge2.json', 'w', encoding='utf-8').write(json.dumps(merge, ensure_ascii=False, indent=1))
io.open('tmp/x0916/cand_new2.json', 'w', encoding='utf-8').write(json.dumps(new, ensure_ascii=False, indent=1))
print('差分の候補 %d ＝ 足し込み %d ／ 新規 %d（id%s〜）' % (len(real), len(merge), len(new), new[0]['newid'] if new else '-'))
