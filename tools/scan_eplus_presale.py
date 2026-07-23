#!/usr/bin/env python3
"""genre:new プールの「発売前(startDateあり)」e+チケットを各公演の専用URLで総点検。

昨日の締切修正は受付中枠のみ対象だったため、発売前枠の発売日ズレ・県違い・
予定枚数終了(死枠)が残っている可能性がある（2026-07-23 ユーザーが山崎ハコ3040で発見）。

読むだけ（修正しない）。各発売前チケットの stored(startDate/date) と実ページの
実在窓を突合し、不一致を報告する。
"""
import json, re, sys, datetime
sys.path.insert(0, 'tools')
from eplus_harvest import fetch, parse_windows

TODAY = datetime.date(2026, 7, 23)

def load():
    h = open('index.html', encoding='utf-8').read()
    m = re.search(r'(?:const|var)\s+EVENTS\s*=\s*(\[.*?\]);', h, re.S) or re.search(r'events\s*=\s*(\[.*?\]);', h, re.S)
    return json.loads(m.group(1))

def main():
    evs = load()
    flags = []
    checked = 0
    for e in evs:
        if e.get('genre') != 'new':
            continue
        for ti, t in enumerate(e.get('tickets') or []):
            sd = t.get('startDate')
            if not sd:                 # 発売前(startDateあり)のみ点検
                continue
            url = t.get('url') or ''
            if 'eplus.jp' not in url:
                continue
            checked += 1
            try:
                html = fetch(url)
            except Exception as ex:
                flags.append((e['id'], ti, 'FETCH-ERR', sd, t.get('date'), str(ex)[:40], t.get('type','')[:36]))
                continue
            ws = parse_windows(html)
            # 予定枚数終了/受付終了 の痕跡（発売前券種が死んでいないか）
            soldout = ('予定枚数終了' in html)
            try:
                sdd = datetime.date(*map(int, sd.split('-')))
            except Exception:
                sdd = None
            # 実ページに stored発売日(sd) と一致する窓があるか
            match = any(w['sd'] == sdd for w in ws) if sdd else False
            future = [w for w in ws if w['ed'] >= TODAY]
            if not future:
                flags.append((e['id'], ti, 'NO-FUTURE-WIN', sd, t.get('date'), '将来窓なし', t.get('type','')[:36]))
            elif not match:
                real = '; '.join(f"{w['kind']}:{w['sd']}→{w['ed']}" for w in ws[:4])
                flags.append((e['id'], ti, 'START-MISMATCH', sd, t.get('date'), real, t.get('type','')[:36]))
    print(f"=== 発売前枠 総点検 (today={TODAY}) 点検{checked}枠 ===")
    print(f"[要確認 {len(flags)}件]")
    for cid, ti, st, sd, dt, info, ty in flags:
        print(f"  id{cid} t{ti} [{st}] stored発売={sd} 締切={dt} | {ty}")
        print(f"        実: {info}")

if __name__ == '__main__':
    main()
