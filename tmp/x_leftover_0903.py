# -*- coding: utf-8 -*-
"""今夜のX投稿に出した公演の「取りこぼし」を、名前でぴあを引いて探す（9/3ぶん）。

夜の便の手順8（day skill）＝**投稿の着地先に公演や枠が欠けていたら、
わざわざ来た人が自分の推しを見つけられない**＝いちばん損なパターン。
🚨ツアーまとめページ（bundle）だけ見ない＝アーティスト名で引き直す
（memory: feedback_pia_bundle_hides_shows）。

対象＝今夜の5本に載せた「明日9/4発売」の名前（tmp/x_draft_0903.txt のリスト行から取る）。
出力は tmp/x_leftover_0903.txt（コンソールに日本語を出さない＝化け読み事故防止）。
"""
import os, re, sys, time

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import pia_kw_search as pks
from pia_missing_audit import load_events, registered_cds, load_excluded, cds

DRAFT = 'tmp/x_draft_0903.txt'
OUT = 'tmp/x_leftover_0903.txt'
WAIT = 5

# 投稿の「【9/4(金)発売】」ブロックの行だけ拾う（9/5・9/6のブロックは対象外）
names, on = [], False
for ln in open(DRAFT, encoding='utf-8'):
    s = ln.strip()
    if s.startswith('【9/4'):
        on = True
        continue
    if s.startswith('【9/5') or s.startswith('【9/6'):
        on = False
        continue
    if not on:
        continue
    m = re.match(r'^\d{1,2}:\d{2}\s+(.+?)／', s)
    if m:
        nm = m.group(1).strip()
        if nm not in names:
            names.append(nm)

events = load_events()
regs = registered_cds(events)
excl = load_excluded()

out = open(OUT, 'w', encoding='utf-8')
out.write('# 9/3夜のX投稿に出した公演の取りこぼし監査（対象 %d名義）\n\n' % len(names))
print('keywords=%d' % len(names))

miss_total = 0
fail = 0
for i, nm in enumerate(names, 1):
    # 検索に効かない飾りを落とす
    kw = re.sub(r'[『』「」【】≪≫＜＞<>]', ' ', nm)
    kw = re.split(r'\s+(?:presents|PRESENTS|Special|SPECIAL)', kw)[0].strip()
    kw = kw[:24].strip()
    if not kw:
        continue
    try:
        hits = pks.search(kw)
        fail = 0
    except Exception as ex:
        fail += 1
        out.write('!! %s 取得失敗 %s\n' % (nm, ex))
        if fail >= 5:
            out.write('!! 5連続で失敗＝中断（ぴあ429の疑い）\n')
            break
        time.sleep(WAIT)
        continue
    # 🚨pks.search() は {url: item} の辞書を返す（リストではない）
    new = []
    for u, h in hits.items():
        got = set(cds(u))
        if not got or (got & regs) or (got & excl):
            continue
        new.append((u, h))
    if new:
        miss_total += len(new)
        out.write('■ %s … 未登録 %d件\n' % (nm, len(new)))
        for u, h in new:
            out.write('   %s | %s | %s\n' % (h.get('status') or '',
                                             (h.get('name') or '')[:46], u))
        out.write('\n')
    out.flush()
    print('[%d/%d] done' % (i, len(names)))
    time.sleep(WAIT)

out.write('\n=== 未登録の候補 合計 %d件 ===\n' % miss_total)
out.close()
print('miss_total=%d -> %s' % (miss_total, OUT))
