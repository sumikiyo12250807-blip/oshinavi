# -*- coding: utf-8 -*-
"""reconcile_eplus の FAIL を実ページどおりに直す（2026-10-16 新設・毎日の --third の後に回す）。

使い方:
  python tools/fix_eplus_fails.py <reconcile_eplus の出力.txt>            # 下見（index.html は読むだけ）
  python tools/fix_eplus_fails.py <reconcile_eplus の出力.txt> --apply    # 当てる（CRLF・NEW_ORDER を保つ）

直す型（10/15 の 140枠の直し tmp/x1015/efx_fix.py を一般化）:
  c-死枠        その枠の窓が「予定枚数終了/完売」→ soldout 印／「受付終了・販売終了」→ soldout＋saleEnded 印
                （DELETE_GATE＝販売終了も消さない）。同じページの受付中/受付前の窓で登録に無いものは足す
  s-売切表示ズレ 受付中の窓が1つに決まれば印を外して窓に合わせる
  b-締切ズレ    同じ発売日の窓（無ければ受付中の窓）が1つに決まれば締切を合わせる
  それ以外（FETCH・g-粒度・f-公演日・b-発売前化・b-発売日ズレ）は報告だけ＝人が見る
"""
import json, re, sys, os, io, copy, datetime, html as H
sys.path.insert(0, 'tools')
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
from eplus_harvest import fetch, parse_ld, fix_half_kana

TODAY = datetime.date.today()
TS = TODAY.isoformat()
_P = re.compile(r'受付期間:(\d{4})/(\d{1,2})/(\d{1,2})\([^)]*\)(\d{1,2}):(\d{2})～(\d{4})/(\d{1,2})/(\d{1,2})\([^)]*\)(\d{1,2}):(\d{2})')
_DEAD = ('予定枚数終了', '受付終了', '販売終了', '完売', '受付は終了')
SCOPE = re.compile(r'（([^（）]*?)公演）')


def flat(x):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', H.unescape(x))).strip()


def blocks(html):
    out = []
    for s in re.split(r'(?=<section class="block-ticket">)', html):
        if not s.startswith('<section class="block-ticket">'):
            continue
        body = s.split('</section>', 1)[0]
        mm = _P.search(flat(body))
        if not mm:
            continue
        g = mm.groups()
        span = re.search(r'<span class="ticket-status__item[^"]*">([^<]+)</span>', body)
        stxt = span.group(1).strip() if span else ''
        if any(w in stxt for w in _DEAD):
            st = 'ended'
        elif '受付中' in stxt:
            st = 'open'
        elif '受付前' in stxt:
            st = 'before'
        else:
            st = 'unknown'
        hd = re.search(r'block-ticket__header[^>]*>(.*?)</header>', body, re.S)
        ht = flat(hd.group(1) if hd else body)
        label = re.sub(r'受付期間.*', '', ht).strip()
        label = re.sub(r'[★☆◇◆■◎●▲△▼▽※]', '', label)
        label = re.sub(r'(先着|抽選)\s*(先着|抽選)', r'\1', label)
        label = re.sub(r'\s+', '', label)
        out.append({'sd': datetime.date(int(g[0]), int(g[1]), int(g[2])), 'st': f'{int(g[3])}:{g[4]}',
                    'ed': datetime.date(int(g[5]), int(g[6]), int(g[7])), 'et': f'{int(g[8])}:{g[9]}',
                    'status': st, 'stxt': stxt, 'label': label})
    return out


def scope_of(ty):
    ms = list(SCOPE.finditer(ty))
    return ms[-1] if ms else None


def set_scope_time(ty, tm):
    s = scope_of(ty)
    if not s or re.search(r'\d{1,2}:\d{2}$', s.group(1)):
        return ty
    return ty[:s.start()] + f'（{s.group(1)} {tm}公演）' + ty[s.end():]


def head_of(ty):
    s = scope_of(ty)
    return ty[:s.end()] if s else re.sub(r'(〜.*|\d{1,2}/\d{1,2}\s+\d{1,2}:\d{2}\s*発売)$', '', ty)


def apply_window(t, W, L):
    for k in ('soldout', 'soldoutSince', 'saleEnded', 'saleEndedSince'):
        t.pop(k, None)
    ty = t['type']
    if L and L.get('time') and W['ed'].isoformat() == L['date']:
        ty = set_scope_time(ty, L['time'])
    if W['sd'] >= TODAY:
        t['type'] = f"{head_of(ty)}{W['sd'].month}/{W['sd'].day} {W['st']}発売"
        t['startDate'] = W['sd'].isoformat()
    else:
        t['type'] = f"{head_of(ty)}〜{W['ed'].month}/{W['ed'].day} {W['et']}"
        if t.get('startDate') and t['startDate'] != W['sd'].isoformat():
            t['startDate'] = W['sd'].isoformat()
    t['date'] = W['ed'].isoformat()


def own_window(t, bl):
    sd, d = t.get('startDate'), t.get('date') or ''
    if sd:
        same = [b for b in bl if b['sd'].isoformat() == sd]
        mm = [b for b in same if b['ed'].isoformat() == d]
        if mm:
            return mm[0], 'sd+ed'
        if len(same) == 1:
            return same[0], 'sd'
    mm = [b for b in bl if b['ed'].isoformat() == d]
    if len(mm) == 1:
        return mm[0], 'ed'
    return None, f'自分の窓が決まらない(sd={sd} date={d} 候補{len(mm)})'


def parse_report(path):
    txt = io.open(path, encoding='utf-8', errors='replace').read()
    out = []
    for m in re.finditer(r'id(\d+) t(\d+) \[([^\]]+)\] ([^\n]*)\n\s+(\S+)', txt):
        out.append({'id': int(m.group(1)), 'ti': int(m.group(2)), 'code': m.group(3), 'detail': m.group(4), 'url': m.group(5)})
    return out


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__); return 2
    fails = parse_report(args[0])
    apply = '--apply' in args
    text = io.open('index.html', encoding='utf-8', newline='').read()
    mo = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
    st = mo.start(1)
    E, end = json.JSONDecoder().raw_decode(text, st)
    EV = {e['id']: e for e in E}
    cache, log, work, added = {}, [], {}, {}

    def T(eid):
        if eid not in work:
            work[eid] = copy.deepcopy(EV[eid]['tickets'])
        return work[eid]

    for f in fails:
        eid, ti, code, u = f['id'], f['ti'], f['code'], f['url']
        if eid not in EV:
            log.append((eid, ti, code, '触らず', '登録に無い')); continue
        t0 = EV[eid]['tickets'][ti]
        if code not in ('c-死枠', 's-売切表示ズレ', 'b-締切ズレ'):
            log.append((eid, ti, code, '報告だけ', f['detail'])); continue
        if u not in cache:
            try:
                cache[u] = fetch(u)
            except Exception as ex:
                cache[u] = None
        html = cache[u]
        if not html:
            log.append((eid, ti, code, '触らず', 'ページが読めない')); continue
        bl = blocks(html)
        ld = parse_ld(html)
        L = ld[0] if len(ld) == 1 else None
        tk = T(eid)[ti]
        before = tk['type']
        if code == 's-売切表示ズレ':
            op = [b for b in bl if b['status'] == 'open' and b['sd'] <= TODAY <= b['ed']]
            W, how = (op[0], 'open1') if len(op) == 1 else own_window(t0, op)
            if not W:
                log.append((eid, ti, code, '触らず', how)); continue
            apply_window(tk, W, L)
            log.append((eid, ti, code, '印を外して合わせた', f"{before} → {tk['type']}")); continue
        if code == 'b-締切ズレ':
            cand = [b for b in bl if b['sd'].isoformat() == t0['startDate']] if t0.get('startDate') \
                else [b for b in bl if b['status'] == 'open' and b['sd'] <= TODAY <= b['ed']]
            if len(cand) != 1 or cand[0]['status'] not in ('open', 'before'):
                log.append((eid, ti, code, '触らず', f'候補の窓{len(cand)}')); continue
            apply_window(tk, cand[0], L)
            log.append((eid, ti, code, '締切を合わせた', f"{before} → {tk['type']}")); continue
        # c-死枠
        W, how = own_window(t0, bl)
        if not W:
            log.append((eid, ti, code, '触らず', how)); continue
        if W['status'] != 'ended':
            log.append((eid, ti, code, '触らず', f"自分の窓は {W['stxt']}")); continue
        if not ('予定枚数終了' in W['stxt'] or '完売' in W['stxt']) and W['ed'] <= TODAY \
                and tk.get('date') == W['ed'].isoformat():
            log.append((eid, ti, code, '触らず', f"登録の締切どおりに終わった（{W['ed']} {W['et']}）＝朝の期限切れで片付く")); continue
        if tk.get('date') != W['ed'].isoformat() and '〜' in tk['type']:
            tk['type'] = f"{head_of(tk['type'])}〜{W['ed'].month}/{W['ed'].day} {W['et']}"
        tk['date'] = W['ed'].isoformat()
        tk['soldout'] = True
        tk.setdefault('soldoutSince', TS)
        if '予定枚数終了' in W['stxt'] or '完売' in W['stxt']:
            log.append((eid, ti, code, '売り切れの印', f"{W['stxt']} 窓{W['sd']}〜{W['ed']} {W['et']}"))
        else:
            tk['saleEnded'] = True
            tk.setdefault('saleEndedSince', TS)
            log.append((eid, ti, code, '販売終了の印', f"{W['stxt']} 窓{W['sd']}〜{W['ed']} {W['et']}"))
        s = scope_of(t0['type'])
        for b in bl:
            if b['status'] not in ('open', 'before') or b['ed'] < TODAY:
                continue
            dup = any(x.get('url') == u and j != ti and (x.get('startDate') == b['sd'].isoformat()
                      or (not x.get('startDate') and x.get('date') == b['ed'].isoformat()))
                      for j, x in enumerate(T(eid)))
            if dup:
                continue
            if not s:
                log.append((eid, ti, code, '足せず', f"公演の括弧が無い {b['label']}")); continue
            ty = f"{b['label']}{s.group(0)}"
            if L and L.get('time') and b['ed'].isoformat() == L['date']:
                ty = set_scope_time(ty, L['time'])
            nt = {'type': '', 'date': b['ed'].isoformat(), 'url': u}
            if b['sd'] >= TODAY:
                nt['type'] = f"{ty}{b['sd'].month}/{b['sd'].day} {b['st']}発売"; nt['startDate'] = b['sd'].isoformat()
            else:
                nt['type'] = f"{ty}〜{b['ed'].month}/{b['ed'].day} {b['et']}"
            nt['type'] = fix_half_kana(nt['type'])
            added.setdefault(eid, []).append((ti, nt))
            log.append((eid, ti, code, '足した', nt['type']))

    for r in log:
        print(*r, sep=' | ')
    n = 0
    for eid, tks in work.items():
        adds = {}
        for ti, nt in added.get(eid, []):
            adds.setdefault(ti, []).append(nt)
        out = []
        for i, t in enumerate(tks):
            out.append(t)
            out.extend(adds.get(i, []))
        if out != EV[eid]['tickets']:
            EV[eid]['tickets'] = out; n += 1
    print(f'直すエントリ {n}')
    if not apply or not n:
        return 0
    compact = text[st:st + 3].startswith('[\r\n{') or text[st:st + 3].startswith('[\n{')
    body = ('[\n' + ',\n'.join(json.dumps(x, ensure_ascii=False, separators=(',', ':')) for x in E) + '\n]') if compact \
        else json.dumps(E, ensure_ascii=False, indent=2)
    if '\r\n' in text[st:st + 3000]:
        body = body.replace('\r\n', '\n').replace('\n', '\r\n')
    io.open('index.html', 'wb').write((text[:st] + body + text[end:]).encode('utf-8'))
    print('当てた')
    return 0


if __name__ == '__main__':
    sys.exit(main())
