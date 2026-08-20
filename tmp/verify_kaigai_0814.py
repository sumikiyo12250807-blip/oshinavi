# -*- coding: utf-8 -*-
"""海外＝エリア化の検算。写経でなく index.html の実ロジックを node で動かして確かめる。"""
import re, sys, json, subprocess
sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import build_ai_page as B

h = open('index.html', encoding='utf-8', newline='').read()
lab = re.search(r'const GENRE_LABEL = \{(.*?)\};', h, re.S).group(1)
grp = re.search(r'const GENRE_GROUPS = \{(.*?)\};', h, re.S).group(1)
print('GENRE_LABEL に kaigai      :', 'kaigai' in lab, '（False が正解）')
print('GENRE_GROUPS に kaigai     :', 'kaigai' in grp, '（False が正解）')
print('data-genre="kaigai" ボタン :', 'data-genre="kaigai"' in h, '（False が正解）')
print('data-region="kaigai" ボタン:', 'data-region="kaigai"' in h, '（True が正解）')
print('PREFECTURE_TO_REGION 台湾  :', '"台湾": "kaigai"' in h, '（True が正解）')
print('ai側 GENRE_LABEL に kaigai :', 'kaigai' in B.GENRE_LABEL, '（False が正解）')
print('ai側 fanevent              :', B.GENRE_LABEL.get('fanevent'))

EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
e = next(x for x in EV if x['id'] == 4259)
print('id4259 genre=%s extra=%s pref=%s' % (e.get('genre'), e.get('extraGenres'), e.get('prefecture')))

# 実物の eventRegions を node で動かす（写経しない）
src = []
for name in ('PREFECTURE_TO_REGION', ):
    src.append('const %s = %s;' % (name, re.search(r'const %s = (\{.*?\});' % name, h, re.S).group(1)))
src.append('const PREF_LIST = Object.keys(PREFECTURE_TO_REGION);')
src.append(re.search(r'(  function parseDateStr\(.*?\n  \})', h, re.S).group(1))
src.append('const today = new Date(2026, 7, 14);')
src.append(re.search(r'(  function isTicketActive\(.*?\n  \})', h, re.S).group(1)
           if re.search(r'  function isTicketActive\(', h) else 'function isTicketActive(){return true;}')
src.append(re.search(r'(  function eventRegions\(ev\) \{.*?\n  \})', h, re.S).group(1))
src.append('const ev = %s;' % json.dumps(e, ensure_ascii=False))
src.append('console.log("id4259 の所属エリア =", JSON.stringify([...eventRegions(ev)]));')
open('tmp/_region_probe.js', 'w', encoding='utf-8').write('\n'.join(src))
print(subprocess.run(['node', 'tmp/_region_probe.js'], capture_output=True, text=True,
                     encoding='utf-8').stdout.strip() or '（node実行失敗）')
