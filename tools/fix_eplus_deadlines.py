#!/usr/bin/env python3
"""genre:new プールのe+受付中チケットの締切を、各公演の専用-P URLから取り直して修正する。

ハーベスタのバグ（複数公演ツアーで日付近傍マッチが隣公演の締切を拾う）で入った
誤った締切を、各チケット自身のe+ページ（1公演＝1ページ）を叩いて正す。

使い方:
  python tools/fix_eplus_deadlines.py            # ドライラン（提案のみ）
  python tools/fix_eplus_deadlines.py --apply    # index.html に適用（tickets の date/type のみ置換）
"""
import json, re, sys, datetime, io
sys.path.insert(0, 'tools')
from eplus_harvest import fetch, parse_windows

TODAY = datetime.date(2026, 7, 22)
APPLY = '--apply' in sys.argv

def load():
    h = open('index.html', encoding='utf-8').read()
    m = re.search(r'(?:const|var)\s+EVENTS\s*=\s*(\[.*?\]);', h, re.S) or re.search(r'events\s*=\s*(\[.*?\]);', h, re.S)
    return h, m, json.loads(m.group(1))

def md(d):
    return f"{d.month}/{d.day}"

def correct_window(url):
    """そのチケットの-Pページを叩き、今開いてる(sd<=today<=ed)枠のうち最終edを返す。無ければNone。"""
    try:
        html = fetch(url)
    except Exception as e:
        return ('ERR', str(e)[:60])
    ws = parse_windows(html)
    if not ws:
        return ('NOWIN', None)
    open_now = [w for w in ws if w['sd'] <= TODAY <= w['ed']]
    if not open_now:
        # 全枠締切済＝もう買えない
        future = [w for w in ws if w['ed'] >= TODAY]
        if future:  # 発売前(sd>today) → このスクリプトの対象外
            return ('PRESALE', None)
        return ('EXPIRED', None)
    w = max(open_now, key=lambda x: x['ed'])
    return ('OK', w)

def main():
    h, m, evs = load()
    changes = []   # (id, ti, old_date, new_date, old_type, new_type)
    flags = []     # (id, ti, status, url)
    for e in evs:
        if e.get('genre') != 'new':
            continue
        for ti, t in enumerate(e.get('tickets') or []):
            if t.get('startDate'):     # 発売前は正確（Fable確認済）→触らない
                continue
            url = t.get('url') or ''
            if 'eplus.jp' not in url:
                continue
            res = correct_window(url)
            st = res[0]
            if st != 'OK':
                flags.append((e['id'], ti, st, url, t.get('type', '')[:40]))
                continue
            w = res[1]
            new_end = w['ed'].isoformat()
            # 締切文字列 "〜M/D HH:MM"（etがあれば時刻付き）
            et = w.get('et') or ''
            new_dl = f"〜{md(w['ed'])}" + (f" {et}" if et else "")
            old_type = t.get('type', '')
            # 既存typeの末尾 "〜..." を差し替え（先頭の "先着一般発売（… 公演）" は保持）
            new_type = re.sub(r'〜.*$', new_dl, old_type) if '〜' in old_type else old_type
            if new_end != t.get('date') or new_type != old_type:
                changes.append((e['id'], ti, t.get('date'), new_end, old_type, new_type))
                if APPLY:
                    t['date'] = new_end
                    t['type'] = new_type

    # レポート
    out = io.StringIO()
    out.write(f"=== e+締切修正 (today={TODAY}) 対象genre:new ===\n")
    out.write(f"\n[修正提案 {len(changes)}件]\n")
    for cid, ti, od, nd, ot, nt in changes:
        out.write(f"  id{cid} t{ti}: date {od} → {nd}\n")
        if ot != nt:
            out.write(f"           type 〜差替: {ot[-24:]}  →  {nt[-24:]}\n")
    out.write(f"\n[要確認フラグ {len(flags)}件]\n")
    for cid, ti, st, url, ty in flags:
        out.write(f"  id{cid} t{ti} [{st}] {ty} | {url}\n")
    print(out.getvalue())

    if APPLY and changes:
        new_json = json.dumps(evs, ensure_ascii=False, indent=2)
        new_h = h[:m.start(1)] + new_json + h[m.end(1):]
        open('index.html.bak_0722_eplus_deadline_fix', 'w', encoding='utf-8').write(h)
        open('index.html', 'w', encoding='utf-8').write(new_h)
        print(f"適用完了 {len(changes)}件（backup: index.html.bak_0722_eplus_deadline_fix）")

if __name__ == '__main__':
    main()
