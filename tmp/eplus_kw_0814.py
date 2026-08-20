# -*- coding: utf-8 -*-
"""e+ キーワード検索で他チャネルの生存を確認（memory: reference_eplus_keyword_search /
feedback_delete_nonpia_blindspot＝ぴあだけ見て消さない）。
一覧のラベルは信用せず、ヒットしたら /sf/detail/ を開いて券種ステータスを読むこと。"""
import sys, json, re, urllib.request, urllib.parse
sys.stdout.reconfigure(encoding='utf-8')

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode('utf-8', 'ignore')


for kw in sys.argv[1:]:
    url = 'https://eplus.jp/sf/search?keyword=' + urllib.parse.quote(kw)
    print('=' * 8, kw, url)
    try:
        h = get(url)
    except Exception as ex:
        print('  取得失敗:', ex)
        continue
    # 埋め込みJSONから公演を拾う
    ids = sorted(set(re.findall(r'/sf/detail/(\d{10}-P\d+)', h)))
    names = re.findall(r'"eventName"\s*:\s*"(.*?)"', h)[:12]
    print('  detailリンク %d件: %s' % (len(ids), ids[:8]))
    for n in names:
        print('   -', n.encode().decode('unicode_escape') if '\\u' in n else n)
    if not ids and not names:
        print('  ヒット無し（e+に掲載なし）')
