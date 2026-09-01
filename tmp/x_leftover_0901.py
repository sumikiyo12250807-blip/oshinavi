# -*- coding: utf-8 -*-
"""X投稿(9/1夜)に出す公演の「ぴあ取りこぼし」総ざらい。

夜の便のpushゲート＝投稿の着地先(oshinavi.jp)に枠が欠けていないか確かめる
（memory: feedback_push 2026-08-26項 / feedback_pia_bundle_hides_shows）。

投稿に名前を出すアーティストだけを、ぴあの rlsInfo.do?kw= で引き直し、
**どのエントリにも登録が無い eventCd** を炙り出す。

  python tmp/x_leftover_0901.py
出力: tmp/x_leftover_0901.txt（UTF-8ファイル。コンソールに日本語を出さない）
"""
import io
import json
import os
import re
import sys
import time
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import pia_kw_search as KW  # noqa: E402

CD_RE = re.compile(r'event(?:Bundle)?Cd=(\w+)')

# 投稿で名前を出すアーティスト（明日9/2発売ぶんを主に、9/3・9/4の大きい名前も少し）
KEYWORDS = [
    # 9/2 音楽
    'BALLISTIK BOYZ', 'ゲシュタルト乙女', 'ダ・カーポ', '古内東子', '松平健',
    '矢野顕子', '辰巳ゆうと', 'ハナレグミ', 'HIRAETH',
    # 9/2 クラシック
    'バッハ・コレギウム・ジャパン', 'フォーレ四重奏団', '札幌交響楽団',
    # 9/2 お笑い
    '米朝一門会',
    # 9/3-9/4 の主な名前
    'パパイヤ鈴木', '加藤登紀子', '小椋佳', '福田こうへい', '秋山黄色', '中村佳穂',
    '新日本フィルハーモニー交響楽団', '桂文珍', 'ヒコロヒー',
    'さだまさし', '杉山清貴', '来生たかお', '一青窈', '清春', '鈴木茂',
    '千住真理子', '野村萬斎', '秋川雅史', '梅沢富美男',
]

WAIT = 3.0


def load_events():
    h = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    m = re.search(r'const EVENTS\s*=\s*(\[.*?\]);', h, re.S)
    return json.loads(m.group(1))


def registered_cds(evs):
    out = set()
    for ev in evs:
        p = (ev.get('links') or {}).get('pia') or ''
        if 'pia' in p:
            out.update(CD_RE.findall(p))
        for t in ev.get('tickets', []):
            u = t.get('url') or ''
            if 'pia' in u:
                out.update(CD_RE.findall(u))
    return out


def load_excluded():
    p = os.path.join(ROOT, 'tools', 'harvest_exclude.json')
    if not os.path.exists(p):
        return set()
    try:
        d = json.load(open(p, encoding='utf-8'))
    except Exception:
        return set()
    out = set()

    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if re.fullmatch(r'b?\d{6,}', str(k)):
                    out.add(str(k))
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
        elif isinstance(x, str):
            if re.fullmatch(r'b?\d{6,}', x):
                out.add(x)
    walk(d)
    return out


def norm(s):
    return re.sub(r'[\s　]+', '', unicodedata.normalize('NFKC', s or '')).lower()


def main():
    evs = load_events()
    reg = registered_cds(evs)
    exc = load_excluded()
    lines = []
    lines.append('# X投稿(9/2発売ぶん)の公演＝ぴあ取りこぼし総ざらい')
    lines.append('# 登録済みぴあコード %d 個 / 引くキーワード %d 語' % (len(reg), len(KEYWORDS)))
    lines.append('')
    hit_total = 0
    miss_total = 0
    fails = 0
    for i, kw in enumerate(KEYWORDS, 1):
        log = []
        try:
            found = KW.search(kw, log)
        except Exception as e:
            lines.append('!! %s : 検索失敗 %s' % (kw, type(e).__name__))
            fails += 1
            if fails >= 5:
                lines.append('!! 連続失敗が多いので中断（429の疑い）')
                break
            time.sleep(WAIT)
            continue
        miss = []
        for url, m in sorted(found.items()):
            codes = CD_RE.findall(url)
            if not codes:
                continue
            if any(c in reg for c in codes):
                continue
            if any(c in exc for c in codes):
                continue
            same = norm(kw) in norm(m.get('title') or '')
            miss.append((codes[0], m.get('title') or '', m.get('rlsdate') or '',
                         m.get('status') or '', url, same))
        hit_total += len(found)
        miss_total += len(miss)
        lines.append('[%d/%d] %s  ぴあヒット%d件 / 未登録%d件'
                     % (i, len(KEYWORDS), kw, len(found), len(miss)))
        for c, t, rd, st, url, same in miss:
            mark = '' if same else '  [別名義/フェス出演の疑い]'
            lines.append('    - %s  %s  発売=%s  状態=%s%s' % (c, t, rd or '(なし)', st, mark))
            lines.append('      %s' % url)
        for l in log:
            lines.append('    %s' % l)
        time.sleep(WAIT)
    lines.append('')
    lines.append('== 合計 ぴあヒット %d件 / 未登録候補 %d件 ==' % (hit_total, miss_total))
    out = os.path.join(ROOT, 'tmp', 'x_leftover_0901.txt')
    io.open(out, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
    print('WROTE', out, 'MISSING=%d' % miss_total)
    return 0


if __name__ == '__main__':
    sys.exit(main())
