# -*- coding: utf-8 -*-
"""検証エージェント2本の「ゼロから再導出した値」と、登録値(tmp/verify_ref_0825.json)を突合する。
エージェントには登録値を見せていないので、ここで初めて答え合わせになる。
"""
import json, io, re, sys, unicodedata
sys.stdout.reconfigure(encoding='utf-8')

ref = json.load(io.open('tmp/verify_ref_0825.json', encoding='utf-8'))
out = {}
for p in ('tmp/verify_out_1_0825.json', 'tmp/verify_out_2_0825.json'):
    out.update(json.load(io.open(p, encoding='utf-8')))

print('登録 %d件 / 再導出 %d件' % (len(ref), len(out)))
missing = [k for k in ref if k not in out]
if missing:
    print('🚨再導出に無いid:', missing)


def pref_set(s):
    s = unicodedata.normalize('NFKC', s or '')
    return set(re.sub(r'[都道府県]$', '', x) for x in re.split(r'[・／/、]', s) if x.strip())


# 登録tickets の締切日(YYYY-MM-DD)集合
def when_dates(slots):
    ds = set()
    for s in slots:
        m = re.search(r'(\d{4})/(\d{1,2})/(\d{1,2})', s.get('when') or '')
        if m:
            ds.add('%s-%02d-%02d' % (m.group(1), int(m.group(2)), int(m.group(3))))
    return ds


issues = []
for k, r in sorted(ref.items(), key=lambda kv: int(kv[0])):
    o = out.get(k)
    if not o or 'error' in o:
        issues.append((k, r['name'], '再導出できず %s' % (o or {}).get('error', '(欠落)')))
        continue

    reg_n = len(r['tickets'])
    own = [t for t in r['tickets'] if True]
    # 別eventCdから持ってきた枠（ticket.url付き）は本エントリのぴあURLには載らない
    n_extra = 0
    if reg_n != o.get('buyable'):
        issues.append((k, r['name'], '枠数 登録%d / 再導出%d' % (reg_n, o.get('buyable'))))

    if r['date'] != o.get('last_perf'):
        issues.append((k, r['name'], '千秋楽 登録%s / 再導出%s' % (r['date'], o.get('last_perf'))))

    pr, po = pref_set(r['prefecture']), set(
        re.sub(r'[都道府県]$', '', x) for x in (o.get('prefs') or []))
    if pr != po and po:
        issues.append((k, r['name'], '県 登録%s / 再導出%s' % (
            '・'.join(sorted(pr)), '・'.join(sorted(po)))))

    reg_d = set(t['date'] for t in r['tickets'] if t.get('date'))
    got_d = when_dates(o.get('slots') or [])
    only_reg = reg_d - got_d
    only_got = got_d - reg_d
    if only_reg:
        issues.append((k, r['name'], '登録にあるが実ページに無い締切 %s' % ','.join(sorted(only_reg))))
    if only_got:
        issues.append((k, r['name'], '実ページにあるが登録に無い締切 %s' % ','.join(sorted(only_got))))

print('\n=== 指摘 %d件 ===' % len(issues))
for k, n, why in issues:
    print('  id%-5s %-34s %s' % (k, (n or '')[:32], why))
