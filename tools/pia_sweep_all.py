# -*- coding: utf-8 -*-
"""【1000件の壁を割る】ぴあ rlsInfo.do の一覧は 100ページ＝1000件で頭打ちになる。
音楽の受付中は在庫4,400件超あるのに600件しか見えず、一覧が五十音順なので
**頭文字の若い側だけ**を毎日拾うことになる（2026-08-24 発見・2026-08-17の「あ行だけ」事故と同型）。

⚠️plan.md に書いた「発売日レンジ rfdy/rtdy で割る」は **効かない**（2026-08-25 実測＝
   件数もバイト数も絞り無しと完全に同一＝パラメータが無視される）。

✅効く軸は詳細検索フォーム search_dtl_input.do にあった2つ（2026-08-25 実測）:
   - sg … サブジャンル（音楽なら 0100102=J-POP・ROCK など10種）
   - rg … 地域（01関東甲信越 / 02関西 / 03中部 / 04九州沖縄 / 05北海道 / 06中国四国 / 07東北 / 08北陸）
   - pf … 都道府県（さらに細かく割りたい時）
   実測: 音楽 受付中 4437件 → sg で割ると 155/3567/262/6/14/8/206/18/94/148（合計4478）。
   まだ1000超えの sg は rg で割る（J-POP・ROCK 3567 → 関東1604… → さらに pf）。

使い方:
  python tools/pia_sweep_all.py <lg> <out.json> [base_filter]
     例) python tools/pia_sweep_all.py 01 tmp/sweep_music.json rlsStatus=0101
  既定 base_filter は rlsIn=03（発売前。在庫が小さいので普通は分割不要＝そのまま1回で走る）

出力は presale_harvest.py と同じ形（new のリスト）＋ buckets に分割の内訳を残す。
🚨カバレッジ（各バケツの想定ページまで到達したか）を必ず表示する。
"""
import re, sys, json, time, html, subprocess, http.client

sys.stdout.reconfigure(encoding='utf-8')

LG = sys.argv[1] if len(sys.argv) > 1 else '01'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'tmp/sweep_%s.json' % LG
BASE = sys.argv[3] if len(sys.argv) > 3 else 'rlsIn=03'

CAP = 1000            # ぴあの頭打ち（100ページ×10件）
LIMIT = 950           # これを超えたらさらに割る（余裕を持たせる）

_conn = None


def _get(path):
    global _conn
    for attempt in (1, 2):
        try:
            if _conn is None:
                _conn = http.client.HTTPSConnection('t.pia.jp', timeout=30)
            _conn.request('GET', path, headers={'User-Agent': 'Mozilla/5.0',
                                                'Connection': 'keep-alive',
                                                'Accept-Encoding': 'identity'})
            r = _conn.getresponse()
            b = r.read().decode('utf-8', 'replace')
            if r.status != 200:
                raise OSError('status %d' % r.status)
            return b
        except Exception:
            try:
                _conn.close()
            except Exception:
                pass
            _conn = None
            if attempt == 2:
                raise
            time.sleep(1.0)


def total_of(filter_str):
    """その絞り込みの総件数。取れなければ None。"""
    b = _get('/pia/rlsInfo.do?lg=%s&%s&page=1' % (LG, filter_str))
    m = re.search(r'全([0-9,]+)件中', b)
    return int(m.group(1).replace(',', '')) if m else None


def sg_list():
    """このジャンル(lg)のサブジャンルコードとラベル。"""
    form = _get('/pia/search_dtl_input.do')
    out = []
    for m in re.finditer(r'<input[^>]*name="sg"[^>]*value="(%s\d+)"[^>]*>' % LG, form):
        v = m.group(1)
        lab = re.search(r'>([^<>]{1,30})<', form[m.end():m.end() + 300])
        out.append((v, html.unescape(lab.group(1)).strip() if lab else ''))
    return out


RG = [('01', '関東甲信越'), ('02', '関西'), ('03', '中部'), ('04', '九州・沖縄'),
      ('05', '北海道'), ('06', '中国・四国'), ('07', '東北'), ('08', '北陸')]


def plan_buckets():
    """1000件を超えないバケツの一覧に割る。割れなかったら警告を残す。"""
    base_total = total_of(BASE)
    print('lg=%s  %s  総件数=%s' % (LG, BASE, base_total))
    if base_total is None:
        return [(BASE, 'ALL', None)], base_total
    if base_total <= LIMIT:
        return [(BASE, 'ALL', base_total)], base_total

    buckets = []
    for sg, lab in sg_list():
        t = total_of('%s&sg=%s' % (BASE, sg))
        time.sleep(0.6)
        if t is None or t == 0:
            continue
        if t <= LIMIT:
            buckets.append(('%s&sg=%s' % (BASE, sg), 'sg=%s %s' % (sg, lab), t))
            continue
        # まだ多い → 地域で割る
        print('  sg=%s %s が %d件 → 地域で割る' % (sg, lab, t))
        for rg, rlab in RG:
            t2 = total_of('%s&sg=%s&rg=%s' % (BASE, sg, rg))
            time.sleep(0.6)
            if not t2:
                continue
            if t2 <= LIMIT:
                buckets.append(('%s&sg=%s&rg=%s' % (BASE, sg, rg),
                                'sg=%s %s / %s' % (sg, lab, rlab), t2))
            else:
                # さらに都道府県で割る
                print('    %s も %d件 → 都道府県で割る' % (rlab, t2))
                for pf in ['%02d' % i for i in range(1, 48)]:
                    t3 = total_of('%s&sg=%s&rg=%s&pf=%s' % (BASE, sg, rg, pf))
                    time.sleep(0.4)
                    if not t3:
                        continue
                    buckets.append(('%s&sg=%s&rg=%s&pf=%s' % (BASE, sg, rg, pf),
                                    'sg=%s %s / %s / pf=%s' % (sg, lab, rlab, pf), t3))
    return buckets, base_total


def run_bucket(filter_str, tmpout):
    r = subprocess.run([sys.executable, 'tools/presale_harvest.py', LG, tmpout, filter_str],
                       capture_output=True, text=True, encoding='utf-8')
    if r.returncode != 0:
        return None, r.stderr[-400:]
    try:
        return json.load(open(tmpout, encoding='utf-8')), ''
    except Exception as e:
        return None, str(e)


def main():
    buckets, base_total = plan_buckets()
    print('\n=== バケツ %d個 ===' % len(buckets))
    for f, lab, t in buckets:
        print('  %-38s %s件' % (lab, t))

    merged, seen = [], set()
    rows = []
    over = []
    for i, (f, lab, t) in enumerate(buckets, 1):
        tmpout = 'tmp/_sweepbucket_%s_%d.json' % (LG, i)
        d, err = run_bucket(f, tmpout)
        if d is None:
            print('[%d/%d] %-34s ❌失敗 %s' % (i, len(buckets), lab, err))
            rows.append({'filter': f, 'label': lab, 'total': t, 'error': err})
            continue
        reach = '%d/%d' % (d.get('fetched_pages', 0), d.get('pages', 0))
        ok = d.get('fetched_pages', 0) >= d.get('pages', 0)
        if not ok:
            over.append(lab)
        print('[%d/%d] %-34s 総%4s 取得%4d ページ到達%s%s'
              % (i, len(buckets), lab[:34], t, d.get('parsed', 0), reach,
                 '' if ok else ' 🚨未到達'))
        for it in d.get('new', []):
            if it['url'] not in seen:
                seen.add(it['url'])
                merged.append(it)
        rows.append({'filter': f, 'label': lab, 'total': t,
                     'parsed': d.get('parsed'), 'pages': d.get('pages'),
                     'fetched_pages': d.get('fetched_pages'),
                     'new': len(d.get('new', []))})

    json.dump({'lg': LG, 'base_filter': BASE, 'base_total': base_total,
               'buckets': rows, 'new': merged},
              open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('\n未掲載(eventCd未登録)の候補 = %d件' % len(merged))
    print('written', OUT)
    if over:
        print('🚨ページ未到達のバケツ:', ', '.join(over))


main()
