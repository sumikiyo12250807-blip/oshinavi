# -*- coding: utf-8 -*-
"""X投稿のライブの総ざらいで見つかった「本当の抜け」を、組み立て用の候補にする（読むだけ・2026-09-15夜）。
入力＝tmp/x0916/audit_real_missing.json（audit_dedup で公演名・公演日が合う登録が無かった分）
分け方（9/14夜の tmp/x0914/audit_cands.py と同じ）:
  足し込み＝候補の公演名が、今あるエントリのアーティスト名とそっくり同じ（NFKC・空白を落として比べる）で、
           そのエントリが1つに決まる時だけ（ツアーは1エントリにまとめる）→ tmp/x0916/cand_merge.json（target 付き）
  新規　　＝それ以外（同じ名前のエントリが日ごとに何本もある繁昌亭なども、足し先が決まらないので新規）
           → tmp/x0916/cand_new.json
新規の id は、index.html の最大 id と last_batch の最大 id_to の次から振る（仮の番号のまま入れない）。
使い方: python tmp/x0916/audit_cands.py
"""
import io
import json
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')


def norm(s):
    return re.sub(r'[\s　]+', '', unicodedata.normalize('NFKC', s or '')).lower()


real = json.load(io.open('tmp/x0916/audit_real_missing.json', encoding='utf-8'))
src = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
lb = json.load(io.open('.claude/state/last_batch.json', encoding='utf-8'))['batches']
by_artist = {}
for e in ev:
    by_artist.setdefault(norm(e.get('artist')), []).append(e)
next_id = max([e['id'] for e in ev] + [b.get('id_to') or 0 for b in lb]) + 1
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
io.open('tmp/x0916/cand_merge.json', 'w', encoding='utf-8').write(json.dumps(merge, ensure_ascii=False, indent=1))
io.open('tmp/x0916/cand_new.json', 'w', encoding='utf-8').write(json.dumps(new, ensure_ascii=False, indent=1))
print('候補 %d ＝ 足し込み %d ／ 新規 %d（id%s〜）' % (len(real), len(merge), len(new), new[0]['newid'] if new else '-'))
