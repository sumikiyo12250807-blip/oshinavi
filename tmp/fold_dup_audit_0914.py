# -*- coding: utf-8 -*-
"""今日（9/14）既存エントリに足した枠が、同じエントリの別の枠と「県・公演日・締切」で重なっていないかを点検する（読むだけ）。
3710 コンサドーレ札幌対大分で、まとめページ（eventBundleCd）経由の枠が、公演ページ（eventCd）の枠と
同じ試合・同じ締切なのに券種名が違うせいで2つずつ並んだ（1つは「■■■車いす…」の化けた名前）。
ぴあは同じ枠を2通りの書き方で出す＝突き合わせは券種名でなく「県・公演日・締切」（feedback_capture_all_deadlines_on_add）。
比べる相手＝9/13の最後のコミットの index.html（今日の足し込み前）。
使い方: python tmp/fold_dup_audit_0914.py
出力: tmp/fold_dup_audit_0914.md
"""
import datetime
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()


def git(*a):
    return subprocess.run(['git'] + list(a), capture_output=True).stdout.decode('utf-8')


def events_of(text):
    return {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', text, re.S).group(1))}


base = git('rev-list', '-1', '--before=2026-09-14 00:00', 'HEAD').strip()
old = events_of(git('show', base + ':index.html'))
new = events_of(io.open('index.html', encoding='utf-8').read())


def visible(t):
    if t.get('soldout'):
        return False
    sd, d = t.get('startDate'), t.get('date') or ''
    return not ((not sd or sd <= TODAY) and d < TODAY)


def key(t):
    """（県 M/D公演）＋その後ろ（〜締切 / 発売日時）＝同じ売り場かの目安。券種名は見ない。"""
    m = re.search(r'（[^（）]*公演）.*$', t.get('type') or '')
    return (m.group(0) if m else t.get('type') or '', t.get('date') or '')


DECOR = re.compile(r'[■□◆◇●○★☆※▼▲]')
out = io.open('tmp/fold_dup_audit_0914.md', 'w', encoding='utf-8')
W = out.write
W('# 今日既存エントリに足した枠の重なり点検（比べる相手 %s）\n\n' % base[:8])
added_n = dup_n = deco_n = 0
for i, e in sorted(new.items()):
    if i not in old:
        continue
    before = {json.dumps(t, ensure_ascii=False, sort_keys=True) for t in old[i].get('tickets') or []}
    added = [t for t in e.get('tickets') or [] if json.dumps(t, ensure_ascii=False, sort_keys=True) not in before]
    if not added:
        continue
    added_n += len(added)
    vis = [t for t in e.get('tickets') or [] if visible(t)]
    lines = []
    for t in added:
        if not visible(t):
            continue
        twins = [u for u in vis if u is not t and key(u) == key(t)]
        if twins:
            dup_n += 1
            lines.append('  - 重なり：%s ｜%s\n    相手：%s\n' % (
                t.get('type'), t.get('url') or '', ' ／ '.join('%s ｜%s' % (u.get('type'), u.get('url') or '') for u in twins)))
        if DECOR.search(t.get('type') or ''):
            deco_n += 1
            lines.append('  - 飾り記号が券種名に残っている：%s\n' % t.get('type'))
    if lines:
        W('- **id%s %s**\n' % (i, (e.get('name') or '')[:40]))
        for ln in lines:
            W(ln)
W('\n今日足した枠 %d / 重なり %d / 飾り記号 %d\n' % (added_n, dup_n, deco_n))
out.close()
print('今日足した枠 %d / 重なり %d / 飾り記号 %d → tmp/fold_dup_audit_0914.md' % (added_n, dup_n, deco_n))
