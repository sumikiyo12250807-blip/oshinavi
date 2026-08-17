# -*- coding: utf-8 -*-
"""新着収集の投入前ゲート（[[feedback_newpool_presale_ratio_gate]]）。

「発売前が枯れた」と言う前に、在庫をどれだけ見たかを数字で出す。2026-08-17に
①発売前の未掲載判定が名前一致で壊れていた（在庫393件中13件しか出ない）
②受付中スイープが音楽4318件中204件＝カバー率4.7%で打ち切られ「あ行」しか見ていなかった
の2つを、投入するまで誰も気づけなかったのが新設の理由。

  python tools/harvest_audit.py                 … 今日のスイープ結果を監査
  python tools/harvest_audit.py --date 0817     … 日付指定
  python tools/harvest_audit.py --ids 4426-4488 … 投入済みidの「発売前/もう売ってる」内訳

カバー率が THRESHOLD 未満のスイープがあれば **exit 1**（＝穴埋めの判断材料にしてはいけない）。
"""
import io, os, re, sys, json, glob, datetime, collections

sys.stdout.reconfigure(encoding='utf-8')

THRESHOLD = 90.0        # カバー率(%) これを切ったら「枯れた」ではなく「見えていない」

ARGS = sys.argv[1:]


def opt(name, default=None):
    return ARGS[ARGS.index(name) + 1] if name in ARGS else default


STAMP = opt('--date') or '%02d%02d' % (datetime.date.today().month, datetime.date.today().day)
IDS = opt('--ids')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)


def load(path):
    try:
        return json.load(io.open(path, encoding='utf-8'))
    except Exception:
        return None


def audit_sweeps():
    rows, bad = [], []
    for f in sorted(glob.glob('tmp/presale_*_%s.json' % STAMP)) + sorted(glob.glob('tmp/open_*_%s.json' % STAMP)):
        d = load(f)
        if not d:
            continue
        total, parsed = d.get('total', 0), d.get('parsed', 0)
        # 🚨判定はページ数で行う。parsed<total は取りこぼしではない
        #   （ぴあは1公演=1行なので同じeventCdが複数行に出る＝URL重複を潰すと必ず減る）。
        #   打ち切りは「最後のページまで行ったか」でしか分からない。
        pages, fetched = d.get('pages'), d.get('fetched_pages')
        if pages:
            cov = 100.0 * min(fetched or 0, pages) / pages
            basis = 'ページ %s/%s' % (fetched, pages)
        else:
            cov = None                       # 旧形式＝ページ情報なし。判定できない
            basis = 'ページ情報なし'
        new = d.get('new', [])
        kind = '発売前' if os.path.basename(f).startswith('presale') else '受付中'
        rows.append((kind, os.path.basename(f), total, parsed, cov, basis,
                     len(new), d.get('new_name_in_db', 0)))
        if cov is not None and cov < THRESHOLD:
            bad.append((os.path.basename(f), basis, cov))

    if not rows:
        print('⚠️ tmp/*_%s.json が見つからない（スイープを回してから実行して）' % STAMP)
        return 1

    print('=== ① ページ到達率と未掲載候補数（%s）===' % STAMP)
    print('  ※「在庫」は行数、「ユニーク」はURL重複を潰した数。ぴあは1公演=1行なので')
    print('    ユニーク<在庫は正常。打ち切りの判定は右の「ページ」で見る。')
    print('  %-6s %-30s %6s %7s %-13s %8s %6s %s'
          % ('種別', 'ファイル', '在庫', 'ユニーク', 'ページ', '到達率', '未掲載', '同名既存'))
    for kind, name, total, parsed, cov, basis, n_new, n_name in rows:
        flag = ' ⚠️' if (cov is not None and cov < THRESHOLD) else ''
        cv = '%7.1f%%%s' % (cov, flag) if cov is not None else '      -  '
        print('  %-6s %-30s %6d %7d %-13s %s %6d %6d'
              % (kind, name, total, parsed, basis, cv, n_new, n_name))

    pre = [r for r in rows if r[0] == '発売前']
    opn = [r for r in rows if r[0] == '受付中']
    print()
    print('  発売前の未掲載 合計 %d件 / 受付中の未掲載 合計 %d件'
          % (sum(r[6] for r in pre), sum(r[6] for r in opn)))

    unknown = [r[1] for r in rows if r[4] is None]
    if unknown:
        print()
        print('ℹ️ ページ情報が無い（旧形式で作られた）ファイル %d本＝打ち切りの有無を判定できない: %s'
              % (len(unknown), ', '.join(unknown)))

    if bad:
        print()
        print('🚨 最後のページまで行っていないスイープが %d本ある＝在庫を見切れていない。' % len(bad))
        print('   ぴあの一覧は名前順なので、打ち切られると「頭文字の若いものだけ」を拾うことになる。')
        for name, basis, cov in bad:
            print('   - %-30s %s (%.1f%%)' % (name, basis, cov))
        print('   → この結果を根拠に「発売前は枯れた」と判断してはいけない。')
        return 1

    print()
    print('✅ 判定できたスイープは全て最後のページまで到達している。')
    return 0


def audit_ids(spec):
    m = re.match(r'(\d+)-(\d+)$', spec)
    if not m:
        print('--ids は 4426-4488 の形で指定して')
        return 1
    lo, hi = int(m.group(1)), int(m.group(2))
    idx = io.open('index.html', encoding='utf-8').read()
    EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', idx, re.S).group(2))
    today = datetime.date.today()

    def d(s):
        mm = re.match(r'(\d{4})-(\d{2})-(\d{2})', s or '')
        return datetime.date(*[int(x) for x in mm.groups()]) if mm else None

    pre, onsale = [], []
    for e in EV:
        if not (lo <= e['id'] <= hi):
            continue
        starts = [x for x in (d(t.get('startDate')) for t in e.get('tickets') or []) if x]
        (pre if [s for s in starts if s > today] else onsale).append((e['id'], e.get('artist', '')))

    n = len(pre) + len(onsale)
    print()
    print('=== ③ 投入 id%d-%d の内訳（全%d件）===' % (lo, hi, n))
    print('  発売前（これから売る） %d件  /  もう売ってる %d件' % (len(pre), len(onsale)))
    if n and len(pre) * 2 < n:
        print('  🚨 発売前が半分未満。OSHINAVIはカウントダウンのサイト＝この比率で投入しない。')
        print('     （[[feedback_presale_first_harvest]] / [[feedback_newpool_presale_ratio_gate]]）')
        return 1
    return 0


rc = 0
if IDS:
    rc |= audit_ids(IDS)
else:
    rc |= audit_sweeps()
sys.exit(rc)
