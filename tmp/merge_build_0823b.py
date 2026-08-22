# -*- coding: utf-8 -*-
"""統合待ちの候補を「既存エントリ＋未登録URL の全部から作り直す」候補JSONに変換する（2026-08-22）。

やり方＝差分を継ぎ足すのではなく、**そのエントリに紐づく全URLを渡して build_pia_entries で
ゼロから再導出する**（[[feedback_bundle_full_rederive]]）。継ぎ足しだと既存側の枠が古いままになる。

入力: tmp/merge_plan_0823.json（tmp/merge_plan_0823.py が作る）
出力: tmp/merge_cand_0823.json（build_pia_entries.py にそのまま渡せる形）
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

plans = json.load(open('tmp/merge_plan_0823.json', encoding='utf-8'))
h = open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
by = {e['id']: e for e in EVENTS}


def canon(u):
    """ぴあの2つのホスト表記を揃える（ticket.pia.jp/pia/event.do と t.pia.jp/pia/event/event.do）。

    🚨ぴあ以外（e+ の eplus.jp/sf/detail/… 等）は絶対に書き換えない。
       最初これを無条件に t.pia.jp へ寄せてしまい、e+ の枠URLが 404 になった（2026-08-22）。
    """
    if not u:
        return None
    if not re.match(r'^https?://(t|ticket)\.pia\.jp/', u):
        return None
    u = re.sub(r'^https?://[^/]+', 'https://t.pia.jp', u)
    return u.replace('/pia/event.do', '/pia/event/event.do')


cands, missing = [], []
for p in plans:
    e = by.get(p['id'])
    if e is None:
        missing.append(p['id'])
        continue
    urls = []
    for u in [(e.get('links') or {}).get('pia')] + [t.get('url') for t in (e.get('tickets') or [])] \
            + [c['url'] for c in p['cand']]:
        cu = canon(u)
        # 券種ページ（ticketInformation.do）は公演ページではないので渡さない
        if cu and 'ticketInformation.do' not in cu and cu not in urls:
            urls.append(cu)
    cands.append({'newid': p['id'], 'artist': e.get('artist') or e.get('name'), 'urls': urls})

io.open('tmp/merge_cand_0823.json', 'w', encoding='utf-8').write(
    json.dumps(cands, ensure_ascii=False, indent=1))
print('候補 %d件 / URL合計 %d / 見つからない id %s' % (
    len(cands), sum(len(c['urls']) for c in cands), missing or 'なし'))
