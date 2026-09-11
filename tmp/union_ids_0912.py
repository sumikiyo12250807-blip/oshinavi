# -*- coding: utf-8 -*-
"""ぴあ照合にかける id を1本にまとめる（読むだけ）。
  ・check_expired の「⚠️要再確認」＝tmp/expired_recheck_0912.txt
  ・check_zero_badge の「31日より先で枠0」＝tmp/zero_ids_0912.txt
いまの index.html に残っていて、ぴあのURLを持つものだけに絞る（削除済み・ぴあ以外は外す）。
使い方: python tmp/union_ids_0912.py
出力: tmp/reconcile_ids_0912.txt（カンマ区切り）
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')


def ids_in(path):
    try:
        txt = io.open(path, encoding='utf-8', errors='replace').read()
    except OSError:
        print('⚠️ 読めない: %s' % path)
        return []
    # 1行目がカンマ区切りの数字列ならそれを使う（番人の --ids 出力もこの形）
    for ln in txt.splitlines():
        if re.fullmatch(r'\s*\d+(\s*,\s*\d+)*\s*', ln):
            return [int(x) for x in re.findall(r'\d+', ln)]
    return []


a = ids_in('tmp/expired_recheck_0912.txt')
b = ids_in('tmp/zero_ids_0912.txt')
src = io.open('index.html', encoding='utf-8').read()
ev = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))}


def has_pia(e):
    L = e.get('links') or {}
    return bool(L.get('pia')) or any('pia.jp' in (t.get('url') or '') for t in e.get('tickets') or [])


u = sorted(set(a) | set(b))
gone = [i for i in u if i not in ev]
nopia = [i for i in u if i in ev and not has_pia(ev[i])]
keep = [i for i in u if i in ev and has_pia(ev[i])]
io.open('tmp/reconcile_ids_0912.txt', 'w', encoding='utf-8').write(','.join(map(str, keep)))
print('要再確認 %d件 ＋ 枠0(31日先) %d件 → 重ねて %d件' % (len(a), len(b), len(u)))
print('  もう無い %d件 %s' % (len(gone), gone))
print('  ぴあURLが無い %d件 %s（ぴあ照合の対象外＝他社の目視が要る）' % (len(nopia), nopia))
print('  ぴあ照合にかける %d件 → tmp/reconcile_ids_0912.txt' % len(keep))
