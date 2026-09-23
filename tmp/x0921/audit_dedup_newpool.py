# -*- coding: utf-8 -*-
"""X投稿のライブの総ざらい（audit_posts.txt・audit_posts2.txt）の「未登録」候補から、見かけの取りこぼしを外す（読むだけ・2026-09-14夜）。
総ざらいの道具は売り場の番号（eventCd／eventBundleCd）だけで突き合わせる＝同じ公演をまとめページの番号と公演の番号で
別々に持っていると「未登録」に見える（「聖夜のメサイア」b2670674 は eventCd=2633164 で登録済みだった）。
ここでは候補ごとに「正規化した公演名が似ている＋公演日が同じ」エントリが index.html にあるかを見る。
使い方: python tmp/x0921/audit_dedup_newpool.py（audit_dedup.py の写し・入力は audit_newpool.txt）
出力: tmp/x0921/audit_dedup_newpool.txt（本当の抜け／登録済みらしい）と tmp/x0921/audit_real_missing_newpool.json（本当の抜けのURL）
"""
import io
import json
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')


def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　・／/「」『』（）()【】〈〉<>!！?？~～\-－ー―、。,.:：&＆"\']', '', s).lower()


def parse(path):
    out = []
    cur = None
    for ln in io.open(path, encoding='utf-8').read().splitlines():
        m = re.match(r'^\s+\[([^\]]*)\] (.+)$', ln)
        if m:
            cur = {'status': m.group(1), 'title': m.group(2), 'src': path.split('/')[-1]}
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


cands = parse('tmp/x0921/audit_newpool.txt')
seen, uniq = set(), []
for c in cands:
    if c.get('url') and c['url'] not in seen:
        seen.add(c['url'])
        uniq.append(c)

src = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))


def iso_dates(s):
    return {'%s-%02d-%02d' % (y, int(mo), int(d)) for y, mo, d in re.findall(r'(\d{4})/(\d{1,2})/(\d{1,2})', s or '')}


def entry_dates(e):
    ds = set()
    for t in e.get('tickets') or []:
        mm = re.search(r'（[^（）]*?((?:R9年\s*)?[\d/〜～・ ]+)公演）', t.get('type') or '')
        if not mm:
            continue
        y = 2027 if 'R9年' in mm.group(1) else 2026
        for mo, d in re.findall(r'(\d{1,2})/(\d{1,2})', mm.group(1)):
            ds.add('%d-%02d-%02d' % (y, int(mo), int(d)))
    ds.add(e.get('date') or '')
    return ds


idx = [(norm((e.get('name') or '') + ' ' + (e.get('artist') or '')), entry_dates(e), e) for e in ev]
real, dup = [], []
for c in uniq:
    nt = norm(c['title'])
    ds = iso_dates(c.get('perf'))
    hit = None
    for n, eds, e in idx:
        if not (ds & eds):
            continue
        if nt and (nt in n or (len(n) > 6 and n[:12] in nt) or nt[:12] in n):
            hit = e
            break
    (dup if hit else real).append((c, hit))

o = io.open('tmp/x0921/audit_dedup_newpool.txt', 'w', encoding='utf-8')
o.write('候補（URL単位）%d ＝ 本当の抜け %d ／ 同じ公演名・公演日の登録あり %d\n\n' % (len(uniq), len(real), len(dup)))
o.write('## 本当の抜け（公演名・公演日が合う登録が無い）\n')
for c, _ in real:
    o.write('- [%s] %s ｜%s ｜%s ｜発売 %s ｜%s\n' % (c['status'], c['title'], c.get('perf'), c.get('venue'), c.get('rls'), c.get('url')))
o.write('\n## 登録済みらしい（売り場の番号が違うだけ）\n')
for c, e in dup:
    o.write('- %s ｜%s → id%s %s\n' % (c['title'], c.get('perf'), e['id'], (e.get('name') or '')[:40]))
o.close()
io.open('tmp/x0921/audit_real_missing_newpool.json', 'w', encoding='utf-8').write(
    json.dumps([c for c, _ in real], ensure_ascii=False, indent=1))
print('候補 %d ＝ 本当の抜け %d ／ 登録済みらしい %d → tmp/x0921/audit_dedup_newpool.txt' % (len(uniq), len(real), len(dup)))
