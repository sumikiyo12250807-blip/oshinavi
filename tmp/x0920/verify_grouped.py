# -*- coding: utf-8 -*-
"""9/20素材（material.md）の各行が post05〜post10 の「時刻 名前／県・県」に1つ残らず入っているか照合する（読むだけ）。"""
import glob, io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
LINE = re.compile(r'^((?:\d{1,2}:\d{2})|時刻未定) (.+)／([^／]*?)(（先行）)?$')
# 今夜の投稿でまとめた名前（素材の名前 → 投稿の名前）
ALIAS = {
    'スーパースターたちによる新春特別コンサート Vol.1': 'スーパースターたちによる新春特別コンサート Vol.1・Vol.2・Vol.3',
    'スーパースターたちによる新春特別コンサート Vol.2': 'スーパースターたちによる新春特別コンサート Vol.1・Vol.2・Vol.3',
    'スーパースターたちによる新春特別コンサート Vol.3': 'スーパースターたちによる新春特別コンサート Vol.1・Vol.2・Vol.3',
    '田辺いちか真打昇進披露の会 ～第15回北九州つながり寄席～': '田辺いちか真打昇進披露の会 ～北九州つながり寄席・博多つながり寄席～',
    '田辺いちか真打昇進披露の会 ～第48回博多つながり寄席～': '田辺いちか真打昇進披露の会 ～北九州つながり寄席・博多つながり寄席～',
    'フットサル国際親善試合<第1戦>': 'フットサル国際親善試合 第1戦・第2戦',
    'フットサル国際親善試合<第2戦>': 'フットサル国際親善試合 第1戦・第2戦',
    '新日本プロレス 赤磐': '新日本プロレス 赤磐大会',
    '新日本プロレス<赤磐大会>': '新日本プロレス 赤磐大会',
    '東京ヤクルトスワローズ 対 広島東洋カープ 2026/10月開催': '東京ヤクルトスワローズ 対 広島東洋カープ 2026/10月開催（車椅子席も）',
    '東京ヤクルトスワローズ 対 広島東洋カープ 2026/10月開催≪車椅子席≫': '東京ヤクルトスワローズ 対 広島東洋カープ 2026/10月開催（車椅子席も）',
    '第16回 ゴッデス・オブ・スターダム ～タッグリーグ戦～ in KORAKUEN vol.1': '第16回 ゴッデス・オブ・スターダム ～タッグリーグ戦～ in KORAKUEN vol.1・vol.2',
    '第16回 ゴッデス・オブ・スターダム ～タッグリーグ戦～ in KORAKUEN vol.2': '第16回 ゴッデス・オブ・スターダム ～タッグリーグ戦～ in KORAKUEN vol.1・vol.2',
}


def rows_of(lines):
    s = set()
    for ln in lines:
        m = LINE.match(ln)
        if not m:
            continue
        t, name, prefs, senko = m.group(1), ALIAS.get(m.group(2), m.group(2)), m.group(3), m.group(4) or ''
        prefs = re.sub(r'\s*\d{1,2}/\d{1,2}〜.*$', '', prefs)
        for p in prefs.split('・'):
            if p in ('', '全国'):
                p = '配信'
            s.add((t, name, p, senko))
    return s


mat = io.open('tmp/x0920/material.md', encoding='utf-8').read()
posts = ''.join(io.open(f, encoding='utf-8-sig').read() + '\n' for f in sorted(glob.glob('tmp/x0920/post0[5-9].txt')) + ['tmp/x0920/post10.txt'])
A = rows_of(mat.splitlines())
B = rows_of(posts.splitlines())
miss = sorted(A - B)
extra = sorted(B - A)
print('素材 %d組 ／ 投稿 %d組 ／ 落ちた %d ／ 素材に無い %d' % (len(A), len(B), len(miss), len(extra)))
for x in miss:
    print('  落ちた', x)
for x in extra:
    print('  素材に無い', x)
