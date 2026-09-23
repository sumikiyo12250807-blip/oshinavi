# -*- coding: utf-8 -*-
"""9/18夜の9本＝動画あり/なしの比較（測るのは2日後＝2026-09-20）。

🚨まとめ型どうしで比べる＝④(動画20秒) と ⑤〜⑨(添付なし)。主役①②③は型が違うので混ぜない。
🚨跳ねた1本を外した検算を必ず並べる。母数＝動画1本 対 なし5本なので勝ち負けは言い切らない。
出力: tmp/x0920/media_ab.md
"""
import csv, io, json, sys
sys.stdout.reconfigure(encoding='utf-8')

rows = list(csv.DictReader(io.open('tmp/x_content_0920.csv', encoding='utf-8')))
d918 = [r for r in rows if r['Date'].strip() == 'Fri, Sep 18, 2026']


def num(r, k):
    try:
        return int(r[k] or 0)
    except ValueError:
        return 0


def clicks(r):
    return num(r, 'URL Clicks') + num(r, 'Permalink Clicks')


# 型で分ける：まとめ＝本文に「まとめよ。」が入る／主役＝入らない
matome = [r for r in d918 if 'まとめよ。' in r['Post text']]
shuyaku = [r for r in d918 if 'まとめよ。' not in r['Post text']]
# 動画の1本＝台帳では④ JPOP/ロック/洋楽のまとめ
video = [r for r in matome if 'JPOP・ロック・洋楽' in r['Post text'] or 'JPOP/ロック' in r['Post text']]
none_ = [r for r in matome if r not in video]


def stat(name, rs):
    imp = sum(num(r, 'Impressions') for r in rs)
    cl = sum(clicks(r) for r in rs)
    eng = sum(num(r, 'Engagements') for r in rs)
    n = len(rs) or 1
    return dict(name=name, n=len(rs), imp=imp, imp_avg=imp / n, clicks=cl,
                clicks_avg=cl / n, ctr=(cl / imp * 100 if imp else 0),
                eng=eng, eng_rate=(eng / imp * 100 if imp else 0))


out = io.open('tmp/x0920/media_ab.md', 'w', encoding='utf-8')
out.write('# 9/18夜の投稿＝動画あり/なしの比較（測定 2026-09-20・投稿の2日後）\n\n')
out.write('対象＝9/18に出した %d本（まとめ %d本／主役 %d本）\n\n' % (len(d918), len(matome), len(shuyaku)))

out.write('## まとめ型どうしの比較（主役は型が違うので混ぜていない）\n\n')
out.write('| 群 | 本数 | 表示 | 1本あたり表示 | クリック | 1本あたりクリック | CTR | 反応率 |\n|---|---|---|---|---|---|---|---|\n')
for s in (stat('動画あり', video), stat('添付なし', none_)):
    out.write('| %s | %d | %d | %.0f | %d | %.1f | %.2f%% | %.2f%% |\n'
              % (s['name'], s['n'], s['imp'], s['imp_avg'], s['clicks'],
                 s['clicks_avg'], s['ctr'], s['eng_rate']))

# 外れ値1本を外した検算（なし群のいちばん高い1本を外す）
if len(none_) > 1:
    top = max(none_, key=lambda r: num(r, 'Impressions'))
    s = stat('添付なし（最高の1本を外す）', [r for r in none_ if r is not top])
    out.write('| %s | %d | %d | %.0f | %d | %.1f | %.2f%% | %.2f%% |\n'
              % (s['name'], s['n'], s['imp'], s['imp_avg'], s['clicks'],
                 s['clicks_avg'], s['ctr'], s['eng_rate']))

out.write('\n## 1本ずつの実数\n\n| 型 | 添付 | 表示 | クリック | 反応 | 冒頭 |\n|---|---|---|---|---|---|\n')
for r in sorted(d918, key=lambda r: -num(r, 'Impressions')):
    kind = 'まとめ' if 'まとめよ。' in r['Post text'] else '主役'
    med = '動画20秒' if r in video else ('なし' if kind == 'まとめ' else '画像')
    head = r['Post text'].split('ピックアップ🎫')[-1].strip()[:28]
    out.write('| %s | %s | %d | %d | %d | %s |\n'
              % (kind, med, num(r, 'Impressions'), clicks(r), num(r, 'Engagements'), head))

out.write('\n## 参考：主役3本（全部画像・動画との比較には使わない）\n\n')
s = stat('主役（画像）', shuyaku)
out.write('本数 %d／表示 %d／1本あたり %.0f／クリック %d／CTR %.2f%%\n'
          % (s['n'], s['imp'], s['imp_avg'], s['clicks'], s['ctr']))
out.close()
print('matome=%d video=%d none=%d shuyaku=%d' % (len(matome), len(video), len(none_), len(shuyaku)))
