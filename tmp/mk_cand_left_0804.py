# -*- coding: utf-8 -*-
"""8/3キーワード監査の取りこぼし（未登録16件）を新規エントリ候補にする。
公演名はぴあの<title>から機械抽出する（手打ちで捏造しない）。
中田カウス2件はid1098に統合済みなので対象外。
既存の同アーティストは「1公演=1エントリ」で登録済み（id3663 横山幸雄(p)等）なので、
育成でまとめず個別エントリにする。
"""
import importlib.util
import io
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'tools'))
spec = importlib.util.spec_from_file_location('bpe', os.path.join(ROOT, 'tools', 'build_pia_entries.py'))
bpe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bpe)

CDS = ['b2669175', 'b2667789', 'b2667996', '2619583', '2607741', '2613845',
       'b2666178', '2617259', '2612630', '2629321', 'b2669751', '2614973',
       'b2669879', '2614626', '2613490', 'b2669353']


def url_of(cd):
    key = 'eventBundleCd' if cd.startswith('b') else 'eventCd'
    return 'https://t.pia.jp/pia/event/event.do?%s=%s' % (key, cd)


def title_of(h):
    """ぴあの<title>は「<公演名>(ヨミガナ) | チケットぴあ[カテゴリ サブのチケット…」形式。
    ①' | 'の前を取る ②末尾のヨミガナ(…)を落とす ③ゼロ幅スペース等を除去。"""
    m = re.search(r'<title>([^<]*)</title>', h or '')
    if not m:
        return None
    t = m.group(1).split('|')[0]
    t = t.replace('​', '').replace('﻿', '').strip()
    t = re.sub(r'[(（][ァ-ヶー・\s]+[)）]\s*$', '', t).strip()   # 末尾のカナ読みだけ落とす
    return t or None


h = io.open(os.path.join(ROOT, 'index.html'), encoding='utf-8', newline='').read()
EVENTS = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
maxid = max(e['id'] for e in EVENTS)
exist_cd = set()
for e in EVENTS:
    blob = json.dumps(e, ensure_ascii=False)
    exist_cd |= set(re.findall(r'event(?:Bundle)?Cd=([0-9a-zA-Z]+)', blob))

cands, log = [], []
for cd in CDS:
    if cd in exist_cd:
        log.append('skip(登録済み) %s' % cd)
        continue
    u = url_of(cd)
    try:
        name = title_of(bpe.fetch(u))
    except Exception as ex:
        log.append('FETCH-ERR %s %s' % (cd, str(ex)[:80]))
        continue
    time.sleep(0.5)
    if not name:
        log.append('公演名が取れない %s' % cd)
        continue
    cands.append({'newid': maxid + 1 + len(cands), 'artist': bpe.norm_fw(name), 'urls': [u]})
    log.append('%d %s | %s' % (cands[-1]['newid'], cands[-1]['artist'], u))

json.dump(cands, io.open('tmp/cand_left_0804.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
io.open('tmp/cand_left_0804.txt', 'w', encoding='utf-8').write('\n'.join(log) + '\n')
print('wrote tmp/cand_left_0804.json  cands=%d' % len(cands))
