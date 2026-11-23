# -*- coding: utf-8 -*-
"""売り場ごとの「載っている割合」を1行ずつ出す（2026-11-24 朝の案2・すちこに出した）。
使い方: python tools/vendor_coverage.py [--pia-open tmp/x1124/pia_open] [--fany tmp/fany_1124.json] [--bleague tmp/x1123/newv_n/bleague/built.json]
  ぴあ＝毎朝の発売中・抽選受付中の一覧（presale_harvest の rows）の eventCd が index.html にあるか
  FANY＝一覧の公演 id（/reception/.../<performance_id>）が index.html にあるか
  B.LEAGUE＝組み上がり（買える試合）の飛び先が index.html にあるか
売り場を叩かない（朝に引いた一覧を読むだけ）。結果は tmp/vendor_coverage.txt にも書く。"""
import argparse, glob, io, json, os, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ap = argparse.ArgumentParser()
ap.add_argument('--pia-open', default='')
ap.add_argument('--fany', default='')
ap.add_argument('--bleague', default='')
a = ap.parse_args()
s = io.open('index.html', encoding='utf-8').read()
out = []
def line(name, n, h):
    out.append('%s %d / %d（%.1f%%）足りない %d' % (name, h, n, 100.0 * h / max(n, 1), n - h))
if a.pia_open:
    have = set(re.findall(r'event(?:Bundle)?Cd=(\w+)', s))
    cds = set()
    for f in glob.glob(os.path.join(a.pia_open, '*.json')):
        d = json.load(io.open(f, encoding='utf-8'))
        for r in d.get('rows') or []:
            m = re.search(r'event(?:Bundle)?Cd=(\w+)', r.get('url') or '')
            if m:
                cds.add(m.group(1))
    line('ぴあ（発売中・抽選受付中）', len(cds), len(cds & have))
if a.fany and os.path.exists(a.fany):
    d = json.load(io.open(a.fany, encoding='utf-8'))
    perfs = d.get('performances') if isinstance(d, dict) else d
    ids = {str(p.get('id')) for p in perfs or [] if p.get('id')}
    have = set(re.findall(r'/reception/\d+/(\d+)', s))
    line('吉本 FANY（公演）', len(ids), len(ids & have))
if a.bleague and os.path.exists(a.bleague):
    B = json.load(io.open(a.bleague, encoding='utf-8'))
    if isinstance(B, dict):
        B = B.get('entries') or []
    urls = set()
    for b in B:
        for t in b.get('tickets') or []:
            if t.get('url'):
                urls.add(t['url'])
    line('B.LEAGUE（買える試合の飛び先）', len(urls), sum(1 for u in urls if u in s))
print('\n'.join(out))
io.open('tmp/vendor_coverage.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
