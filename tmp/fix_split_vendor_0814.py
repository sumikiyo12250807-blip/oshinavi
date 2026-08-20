# -*- coding: utf-8 -*-
"""saleEnded の判定を**枠の売り手ごと**にやり直す（2026-08-14・検証エージェントの指摘）。

前版の誤り: 枠の `ticket.url` が e+ なのに、エントリの links.pia（ぴあ）と突合していた。
ぴあは在庫を持っていないので「予定枚数終了」が出るはずがなく、e+で実際は売り切れている枠を
「販売終了」に格下げしてしまった（工藤静香の釧路8/15・倉吉8/22・奥州8/29）。
＝[[feedback_delete_nonpia_blindspot]]「ぴあで0枠は判断根拠にならない」と同じ罠。

直し: 枠ごとに照合先を切り替える。
  ticket.url が eplus.jp → tools/eplus_detail.py（その公演ページの券種ステータス）
  それ以外              → ぴあ（links.pia を公演日＋県で突合。前版のロジック）
判定は**双方向**＝売り切れが確認できたら saleEnded を外す／確認できなければ付ける。

使い方: python tmp/fix_split_vendor_0814.py [--apply]
"""
import re, sys, json, datetime, subprocess, os
sys.stdout.reconfigure(encoding='utf-8')

APPLY = '--apply' in sys.argv
TODAY = datetime.date.today().isoformat()
SOLD = re.compile(r'予定枚数終了|完売|売切')
ENV = dict(os.environ, PYTHONIOENCODING='utf-8')
_cache = {}


def eplus_statuses(url):
    """e+個別公演ページの全券種ステータス（別実装のツールで取る）。"""
    if url in _cache:
        return _cache[url]
    p = subprocess.run([sys.executable, 'tools/eplus_detail.py', url],
                       capture_output=True, text=True, encoding='utf-8', env=ENV, timeout=120)
    out = p.stdout or ''
    if '[取得失敗]' in out:
        _cache[url] = None
        return None
    sts = re.findall(r'^\s{4}\[.*?\]\s+(\S+)\s+\|', out, re.M)
    _cache[url] = sts
    return sts


h = open('index.html', encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = json.loads(m.group(2))

restored, kept_se, skipped = [], [], []
for ev in EV:
    for t in ev.get('tickets') or []:
        if not t.get('soldout'):
            continue
        u = t.get('url') or ''
        if 'eplus.jp' not in u:
            continue                      # ぴあ由来の枠は前版の判定のまま（公演日＋県で突合済み）
        sts = eplus_statuses(u)
        if sts is None:
            skipped.append((ev['id'], (t.get('type') or '')[:40], 'e+ページ取得失敗(404等)'))
            continue
        sold = any(SOLD.search(s) for s in sts)
        if sold and t.get('saleEnded'):
            t.pop('saleEnded', None)
            t.pop('saleEndedSince', None)
            restored.append((ev['id'], (ev.get('name') or '')[:22], (t.get('type') or '')[:40],
                             '／'.join(sorted(set(sts)))[:36]))
        elif not sold and not t.get('saleEnded'):
            t['saleEnded'] = True
            t['saleEndedSince'] = TODAY
            kept_se.append((ev['id'], (ev.get('name') or '')[:22], (t.get('type') or '')[:40],
                            '／'.join(sorted(set(sts)))[:36]))

print('【予定枚数終了に戻す（e+が売り切れと言っている）】%d枠' % len(restored))
for r in restored:
    print('  id%-5s %-22s %s' % (r[0], r[1], r[2]))
    print('        e+実文言: %s' % r[3])
print('\n【新たに販売終了にする（e+に売切表示なし）】%d枠' % len(kept_se))
for r in kept_se:
    print('  id%-5s %-22s %s' % (r[0], r[1], r[2]))
    print('        e+実文言: %s' % r[3])
print('\n【裏取りできず据え置き】%d枠' % len(skipped))
for r in skipped:
    print('  id%-5s %s … %s' % (r[0], r[1], r[2]))

if (restored or kept_se) and APPLY:
    new_arr = json.dumps(EV, ensure_ascii=False, indent=2).replace('\n', NL)
    open('index.html.bak_0814_vendor', 'w', encoding='utf-8', newline='').write(h)
    open('index.html', 'w', encoding='utf-8', newline='').write(
        h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
    print('\n→ 適用（backup index.html.bak_0814_vendor）')
elif restored or kept_se:
    print('\n（--apply で適用）')
