# -*- coding: utf-8 -*-
"""楽天の枠を「直したビルダー」で作り直し、いま登録されている枠と突き合わせる。

  python tmp/audit_rakuten_split_0910.py            # 監査だけ（書き込まない）
  python tmp/audit_rakuten_split_0910.py --write    # index.html の楽天枠を差し替える

狙い＝2026-09-09 にユーザーが見つけた「作られた締切」を全部つぶす。
販売期間に終わりが書かれていない窓に max(カードの締切) を流用していたので、
複数公演を1枠にまとめた所だけ、早い公演に千秋楽の締切が付いていた。
"""
import argparse
import json
import re
import sys
import urllib.parse

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_harvest as RH
import build_rakuten_entries as B

RAKUTEN = re.compile(r'ticket\.rakuten\.co\.jp')


def raw_url(u):
    """Deep Link から素の楽天URLを取り出す。"""
    m = re.search(r'murl=([^&]+)', u or '')
    if m:
        return urllib.parse.unquote(m.group(1))
    return u or ''


def is_rakuten(u):
    return bool(RAKUTEN.search(raw_url(u)))


def load_events(path='index.html'):
    h = open(path, encoding='utf-8').read()
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
    return h, m, json.loads(m.group(2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--out', default='tmp/rakuten_split_report_0910.txt')
    args = ap.parse_args()

    h, m, events = load_events()

    # ① 楽天の枠を持つエントリと、そのエントリが使っている素の楽天URLを集める
    targets = []
    for e in events:
        urls, slots = [], []
        for i, t in enumerate(e.get('tickets') or []):
            if is_rakuten(t.get('url')):
                slots.append(i)
                u = raw_url(t['url'])
                if u not in urls:
                    urls.append(u)
        lr = ((e.get('links') or {}).get('rakuten')) or ''
        if is_rakuten(lr) and raw_url(lr) not in urls:
            urls.append(raw_url(lr))
        if slots:
            targets.append({'e': e, 'urls': urls, 'slots': slots})

    sys.stderr.write('楽天の枠を持つエントリ %d件 / 素URL %d本\n'
                     % (len(targets), len({u for t in targets for u in t['urls']})))

    # ② 実ページを引く（同じURLは1回だけ）
    cache = {}
    for t in targets:
        for u in t['urls']:
            if u in cache:
                continue
            try:
                cache[u] = RH.parse_page(u, RH.fetch(u))
            except Exception as ex:
                cache[u] = None
                sys.stderr.write('  FETCH失敗 %s (%s)\n' % (u, ex))

    # ③ 直したビルダーで作り直して突合
    out = []
    n_changed = 0
    for t in targets:
        e = t['e']
        recs = [cache[u] for u in t['urls'] if cache.get(u) and cache[u].get('perfs')]
        cur = [e['tickets'][i] for i in t['slots']]
        if not recs:
            out.append({'id': e['id'], 'name': e['name'], 'status': 'FETCH不可',
                        'cur': cur, 'new': None})
            continue
        ne, why = B.build(recs, e['id'])
        new = (ne or {}).get('tickets') if ne else None
        same = (new is not None
                and [(x['type'], x['date']) for x in cur] == [(x['type'], x['date']) for x in new])
        if not same:
            n_changed += 1
        out.append({'id': e['id'], 'name': e['name'],
                    'status': '一致' if same else ('作り直し不可(%s)' % why if new is None else '差分あり'),
                    'cur': cur, 'new': new})

    with open(args.out, 'w', encoding='utf-8') as f:
        for r in out:
            if r['status'] == '一致':
                continue
            f.write('\n=== id=%s %s [%s]\n' % (r['id'], r['name'][:50], r['status']))
            for x in r['cur']:
                f.write('   OLD %s | date=%s%s\n'
                        % (x['type'], x['date'], ' saleEndUnknown' if x.get('saleEndUnknown') else ''))
            for x in (r['new'] or []):
                f.write('   NEW %s | date=%s%s\n'
                        % (x['type'], x['date'], ' saleEndUnknown' if x.get('saleEndUnknown') else ''))
        f.write('\n=== 集計: 対象 %d件 / 一致 %d件 / 要変更 %d件 ===\n'
                % (len(out), len(out) - n_changed, n_changed))
    print('対象 %d件 / 一致 %d件 / 要変更 %d件 → %s'
          % (len(out), len(out) - n_changed, n_changed, args.out))
    json.dump(out, open('tmp/rakuten_split_0910.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)

    if not args.write:
        return 0

    # ④ 楽天の枠だけ差し替える（ぴあ/e+/ローチケの枠には触らない）
    import datetime
    fix = {r['id']: r['new'] for r in out if r['status'] == '差分あり' and r['new']}
    applied = 0
    for t in targets:
        e = t['e']
        new = fix.get(e['id'])
        if not new:
            continue
        at = t['slots'][0]
        keep = [x for i, x in enumerate(e['tickets']) if i not in set(t['slots'])]
        e['tickets'] = keep[:at] + list(new) + keep[at:]
        applied += 1
    bak = 'index.html.bak_%s_rakuten_split' % datetime.date.today().strftime('%m%d')
    open(bak, 'w', encoding='utf-8').write(h)
    arr = json.dumps(events, ensure_ascii=False, indent=2)
    open('index.html', 'w', encoding='utf-8').write(
        h[:m.start()] + m.group(1) + arr + m.group(3) + h[m.end():])
    print('差し替え %d件（backup: %s）' % (applied, bak))
    return 0


if __name__ == '__main__':
    sys.exit(main())
