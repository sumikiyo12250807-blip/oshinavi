# -*- coding: utf-8 -*-
"""soldout枠を「予定枚数終了」と「販売終了」に仕分ける（ユーザー選択 2026-08-14）。

判定は**枠ごと**にぴあ実ページと突合する（エントリ単位の一括マークが誤りの原因だった）:
  登録枠のバッジから「（県 M/D公演）」を取り出し、ぴあ券種の perfdate+pref と一致する行を探す。
  一致行の statustext が
    予定枚数終了/完売/売切  → そのまま soldout（バッジ「予定枚数終了」）
    それ以外(販売終了/受付終了/抽選受付終了) → saleEnded:true を追加（バッジ「販売終了」）
  一致行が見つからない枠は**触らない**（機械で確定できないものを動かさない）。

使い方: python tmp/split_saleended_0814.py [--apply]
"""
import re, sys, json, datetime, time, subprocess, os
sys.stdout.reconfigure(encoding='utf-8')


def pia_rows(url):
    """pia_tickets.py は関数を持たないスクリプトなので、別プロセスで叩いてJSONで受ける
    （＝build系とは別実装で照合する。memory: feedback_verify_independent_not_anchored）。"""
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    p = subprocess.run([sys.executable, 'tools/pia_tickets.py', url, '--all', '--json'],
                       capture_output=True, text=True, encoding='utf-8', env=env, timeout=120)
    if p.returncode != 0:
        raise RuntimeError((p.stderr or '')[:120])
    d = json.loads(p.stdout)
    return d if isinstance(d, list) else (d.get('rows') or d.get('tickets') or [])

APPLY = '--apply' in sys.argv
TODAY = datetime.date.today().isoformat()
SOLD = re.compile(r'予定枚数終了|完売|売切')
PREF = re.compile(r'(北海道|青森|岩手|宮城|秋田|山形|福島|茨城|栃木|群馬|埼玉|千葉|東京|神奈川|'
                  r'新潟|富山|石川|福井|山梨|長野|岐阜|静岡|愛知|三重|滋賀|京都|大阪|兵庫|奈良|'
                  r'和歌山|鳥取|島根|岡山|広島|山口|徳島|香川|愛媛|高知|福岡|佐賀|長崎|熊本|'
                  r'大分|宮崎|鹿児島|沖縄|台湾)')

h = open('index.html', encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = json.loads(m.group(2))


def pia_urls(ev):
    u = (ev.get('links') or {}).get('pia')
    return [u] if u else []


def badge_key(t):
    """バッジの「（県 M/D公演）」「（県 M/D〜M/D公演）」から (県, 開始(M,D), 終了(M,D)) を取る。
    複数県はNone（機械で確定しない）。"""
    ty = t.get('type') or ''
    mm = re.search(r'（([^（）]*?)\s*(?:R\d+年\s*)?(\d{1,2})/(\d{1,2})'
                   r'(?:〜(?:R\d+年\s*)?(\d{1,2})/(\d{1,2}))?公演）', ty)
    if not mm:
        return None
    prefs = PREF.findall(mm.group(1))
    if len(prefs) != 1:
        return None
    s = (int(mm.group(2)), int(mm.group(3)))
    e = (int(mm.group(4)), int(mm.group(5))) if mm.group(4) else s
    return (prefs[0], s, e)


changed, untouched, kept = [], [], []
targets = [e for e in EV if any(t.get('soldout') for t in (e.get('tickets') or []))]
print('soldout枠を持つエントリ', len(targets), '件を枠ごとに突合する')

for ev in targets:
    urls = pia_urls(ev)
    if not urls:
        untouched.append((ev['id'], 'ぴあURL無し'))
        continue
    try:
        rows = pia_rows(urls[0])
    except Exception as ex:
        untouched.append((ev['id'], 'ぴあ取得失敗 %s' % ex))
        continue
    time.sleep(1.2)
    # 県 → [(開始(M,D), 終了(M,D), statustext)]。ぴあ側も perfdate〜perf_end の期間を持つ
    idx = {}
    for r in rows:
        pd, pe = r.get('perfdate') or '', r.get('perf_end') or ''
        for pr in PREF.findall((r.get('pref') or '') + ' ' + (r.get('venue') or '')):
            if not pd:
                continue
            try:
                s = tuple(int(x) for x in pd.split('-')[1:3])
                e = tuple(int(x) for x in pe.split('-')[1:3]) if pe else s
            except ValueError:
                continue
            idx.setdefault(pr, []).append((s, e, r.get('statustext') or ''))
    for t in ev.get('tickets') or []:
        if not t.get('soldout'):
            continue
        k = badge_key(t)
        if not k:
            untouched.append((ev['id'], 'バッジから県/公演日を確定できない: %s' % (t.get('type') or '')[:44]))
            continue
        pr, bs, be = k[0], k[1], k[2]
        # 期間が重なるぴあ券種を全部拾う（単日は自分自身と重なる）
        sts = [st for (s, e, st) in idx.get(pr, []) if not (e < bs or s > be)]
        if not sts:
            # ぴあが券種ごと下げていて売り切れの裏が取れない。強い主張（予定枚数終了＝売り切れた）は
            # できないが、締切が過去なら「販売は終わった」だけは事実なので弱いほうの表示に倒す。
            if (t.get('date') or '9999') < TODAY:
                t['saleEnded'] = True
                t['saleEndedSince'] = TODAY
                changed.append((ev['id'], (ev.get('name') or '')[:26], (t.get('type') or '')[:44],
                                'ぴあに券種なし・締切(%s)は過去' % t.get('date')))
            else:
                untouched.append((ev['id'], 'ぴあに該当公演の券種が無い: %s' % (t.get('type') or '')[:44]))
            continue
        if any(SOLD.search(s) for s in sts):
            kept.append((ev['id'], (t.get('type') or '')[:44]))
        else:
            t['saleEnded'] = True
            t['saleEndedSince'] = TODAY
            changed.append((ev['id'], (ev.get('name') or '')[:26], (t.get('type') or '')[:44],
                            '／'.join(sorted(set(sts)))[:40]))

print('\n【販売終了に切替】%d枠' % len(changed))
for r in changed:
    print('  id%-5s %-26s %s' % (r[0], r[1], r[2]))
    print('        ぴあ実文言: %s' % r[3])
print('\n【予定枚数終了のまま】%d枠' % len(kept))
for r in kept:
    print('  id%-5s %s' % (r[0], r[1]))
print('\n【触らなかった】%d件' % len(untouched))
for r in untouched:
    print('  id%-5s %s' % (r[0], r[1]))

if changed and APPLY:
    new_arr = json.dumps(EV, ensure_ascii=False, indent=2).replace('\n', NL)
    open('index.html.bak_0814_split', 'w', encoding='utf-8', newline='').write(h)
    open('index.html', 'w', encoding='utf-8', newline='').write(
        h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
    print('\n→ 適用（backup index.html.bak_0814_split）')
elif changed:
    print('\n（--apply で適用）')
