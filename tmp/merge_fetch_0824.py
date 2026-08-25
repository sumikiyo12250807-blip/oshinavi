# -*- coding: utf-8 -*-
"""統合待ちのエントリを、紐づく全URLから**1本ずつ**再導出する（2026-08-24 朝）。

🚨 build_pia_entries に複数URLをまとめて渡すと2本目以降の枠に ticket.url が付かず、
   「その枠を売っていないページ」に飛ぶ（feedback_build_pia_multiurl_loses_ticket_url）。
   道具側は未修正なので、ここで**URLを1本ずつ渡して**、links.pia と違うURLから来た枠に
   飛び先を刻む。刻めば reconcile の STALE も「別の売り場から来た枠」と読み分けられる。

入力: tmp/merge_plan_0824.json
出力: tmp/merge_fetched_0824.json  {entry_id: [ticket, ...]}
"""
import io
import json
import os
import re
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

PLAN = 'tmp/merge_plan_0824.json'
OUT = 'tmp/merge_fetched_0824.json'


def canon(u):
    """ぴあの2つのホスト表記を揃える。ぴあ以外（e+等）は絶対に書き換えない。"""
    if not u:
        return None
    if 't.pia.jp' not in u and 'ticket.pia.jp' not in u:
        return u
    m = re.search(r'(eventCd|eventBundleCd)=(\w+)', u)
    return 'https://t.pia.jp/pia/event/event.do?%s=%s' % (m.group(1), m.group(2)) if m else u


def main():
    plans = json.load(io.open(PLAN, encoding='utf-8'))
    h = io.open('index.html', encoding='utf-8', newline='').read()
    EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
    by = {e['id']: e for e in EV}

    done = {}
    if os.path.exists(OUT):
        done = json.load(io.open(OUT, encoding='utf-8'))
        print('(途中まで %d件ぶんの結果あり。続きから)' % len(done))

    t_all = time.time()
    for n, p in enumerate(plans, 1):
        eid = p['id']
        if str(eid) in done:
            continue
        base = canon((by[eid].get('links') or {}).get('pia'))
        got = []
        for u in [canon(x) for x in p['urls']]:
            cand = [{'newid': 900000 + eid, 'artist': p.get('artist') or '', 'urls': [u]}]
            io.open('tmp/_merge_one.json', 'w', encoding='utf-8').write(
                json.dumps(cand, ensure_ascii=False))
            r = subprocess.run([sys.executable, 'tools/build_pia_entries.py', 'tmp/_merge_one.json'],
                               capture_output=True)
            if r.returncode != 0:
                print('  !! id=%d 取得失敗 %s' % (eid, u))
                continue
            try:
                built = json.loads(r.stdout.decode('utf-8'))
            except Exception as ex:
                print('  !! id=%d パース失敗 %s %s' % (eid, u, ex))
                continue
            for b in built:
                for t in b.get('tickets') or []:
                    if u != base and not t.get('url'):
                        t['url'] = u
                    got.append(t)
        done[str(eid)] = got
        json.dump(done, io.open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('[%2d/%d] id=%-5d %-22s URL%d本 → %d枠 (%.0fs)' % (
            n, len(plans), eid, (p.get('artist') or '')[:22], len(p['urls']), len(got),
            time.time() - t_all))
        sys.stdout.flush()
    print('完了 → %s' % OUT)


if __name__ == '__main__':
    main()
