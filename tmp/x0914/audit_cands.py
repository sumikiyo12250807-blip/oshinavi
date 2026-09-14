# -*- coding: utf-8 -*-
"""X投稿のライブの総ざらいで見つかった「本当の抜け」を、組み立て用の候補にする（読むだけ・2026-09-14夜）。
入力＝tmp/x0914/audit_real_missing.json（公演名・公演日で登録と突き合わせて残った53件）
　　＋ audit_dedup の取り違え3件（ウィーン・フォルクスオーパー 1/10 愛知・日本フィル第九 阪哲朗・日本フィル コバケン・ワールド）
分け方:
  足し込み＝候補の公演名が、今あるエントリのアーティスト名とそっくり同じ（NFKC・空白を落として比べる）で、
           そのエントリが1つに決まる時だけ（ツアーは1エントリにまとめる）→ tmp/x0914/cand_merge.json（target 付き）
  新規　　＝それ以外（同じ名前のエントリが日ごとに何本もある繁昌亭なども、足し先が決まらないので新規）
           → tmp/x0914/cand_new.json（newid＝今の最大id+1 から）
使い方: python tmp/x0914/audit_cands.py
"""
import io
import json
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')
EXTRA_URLS = {
    'https://ticket.pia.jp/pia/event.do?eventCd=2541381',      # ウィーン・フォルクスオーパー ニューイヤー 1/10 愛知
    'https://ticket.pia.jp/pia/event.do?eventBundleCd=b2670958',  # 日本フィル 第九 阪哲朗 12/20
    'https://ticket.pia.jp/pia/event.do?eventCd=2617957',      # 日本フィル コバケン・ワールド 9/27
}


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


real = json.load(io.open('tmp/x0914/audit_real_missing.json', encoding='utf-8'))
have = {c['url'] for c in real}
for c in parse('tmp/x0914/audit_posts2.txt'):
    if c.get('url') in EXTRA_URLS and c['url'] not in have:
        real.append(c)
        have.add(c['url'])

src = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
by_artist = {}
for e in ev:
    by_artist.setdefault(norm(e.get('artist')), []).append(e)
next_id = max(e['id'] for e in ev) + 1
tmp_id = 99001


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
io.open('tmp/x0914/cand_merge.json', 'w', encoding='utf-8').write(json.dumps(merge, ensure_ascii=False, indent=1))
io.open('tmp/x0914/cand_new.json', 'w', encoding='utf-8').write(json.dumps(new, ensure_ascii=False, indent=1))
print('候補 %d ＝ 足し込み %d ／ 新規 %d（id%s〜）' % (len(real), len(merge), len(new), new[0]['newid'] if new else '-'))
