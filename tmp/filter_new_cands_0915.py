# -*- coding: utf-8 -*-
"""スイープの「未掲載候補」から、本当に未登録のものだけを残す（読むだけ・2026-09-15 朝）。
filter_new_cands_0914.py の日付違い＋ジャンル(lg)を引数で渡せるようにした
（sweep_music_0101_0914.json のようにファイル名から lg が取れない形があるため）。

「eventCd が登録に無い」だけでなく「正規化した名前 × 公演日」でも当てて、全日程が登録済みなら外す。
🚨名前が違っても対バン名・フェス名で登録済みのことがある＝投入前の check_badges／reconcile と併せて見る。

使い方: python tmp/filter_new_cands_0915.py <globパターン> <出力名> [lg]
例:     python tmp/filter_new_cands_0915.py tmp/sweep_music_0101_0914.json uk01 01
出力: tmp/cands_<出力名>_0915.json（build_pia_entries にそのまま渡せる形）＋ .txt
"""
import glob
import io
import json
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')
PAT = sys.argv[1]
TAG = sys.argv[2]
LG_ARG = sys.argv[3] if len(sys.argv) > 3 else None

src = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
lb = json.load(io.open('.claude/state/last_batch.json', encoding='utf-8'))['batches']


def norm(s):
    s = unicodedata.normalize('NFKC', s or '').lower()
    return re.sub(r'[\s　・･,，.。!！?？~〜\-—–_/／\(\)（）\[\]【】「」『』"\']', '', s)


have, codes = set(), set()
for e in ev:
    n = norm(e.get('artist') or e.get('name'))
    for u in [(e.get('links') or {}).get('pia') or ''] + [t.get('url') or '' for t in (e.get('tickets') or [])]:
        codes |= set(re.findall(r'event(?:Bundle)?Cd=(\w+)', u))
    for t in e.get('tickets') or []:
        mm = re.search(r'（([^（）]*)公演）', t.get('type') or '')
        if not mm:
            continue
        y = 2026
        for r9, mo, dd in re.findall(r'(R9年\s*)?(\d{1,2})/(\d{1,2})', mm.group(1)):
            if r9:
                y = 2027
            have.add((n, '%04d-%02d-%02d' % (y, int(mo), int(dd))))

seen, out, lines = set(), [], []
# id は本番の番号で振る＝いまの最大idと last_batch の最大 id_to の次から。削除済みidは再利用しない
nid = max([e['id'] for e in ev] + [b.get('id_to') or 0 for b in lb])
files = sorted(glob.glob(PAT))
skipped_reg = 0
for p in files:
    lg = LG_ARG or p.replace('\\', '/').split('/')[-1].split('_')[1]
    d = json.load(io.open(p, encoding='utf-8'))
    for r in d.get('new') or []:
        url = r.get('url') or ''
        mcd = re.search(r'event(?:Bundle)?Cd=(\w+)', url)
        cd = mcd.group(1) if mcd else ''
        if not cd or cd in codes or cd in seen:
            continue
        n = norm(r.get('artist'))
        days = ['%s-%02d-%02d' % (y, int(mo), int(dd))
                for y, mo, dd in re.findall(r'(\d{4})/(\d{1,2})/(\d{1,2})', r.get('perfdate') or '')]
        reg = [x for x in days if (n, x) in have]
        if days and len(reg) == len(days):
            skipped_reg += 1
            lines.append('  ⏭ 登録済み lg=%s %-26s %s' % (lg, (r.get('artist') or '')[:26], days))
            continue
        seen.add(cd)
        nid += 1
        out.append({'newid': nid, 'artist': r.get('artist'), 'urls': [url], '_lg': lg,
                    '_perfdate': r.get('perfdate'), '_rlsdate': r.get('rlsdate'), '_pref': r.get('pref')})
        lines.append('  ✅ 候補   lg=%s %-26s 発売%s 公演%s %s' % (
            lg, (r.get('artist') or '')[:26], r.get('rlsdate'), days or r.get('perfdate'), url))

json.dump(out, io.open('tmp/cands_%s_0915.json' % TAG, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
io.open('tmp/cands_%s_0915.txt' % TAG, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('読んだファイル %d本 / 本当に未登録の候補 %d件（名前×公演日で登録済み %d件を外した）→ tmp/cands_%s_0915.json' % (
    len(files), len(out), skipped_reg, TAG))
if out:
    print('id %s〜%s' % (out[0]['newid'], out[-1]['newid']))
