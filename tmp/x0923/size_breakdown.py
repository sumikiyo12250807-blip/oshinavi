# -*- coding: utf-8 -*-
"""index.html の重さの内訳と、「詰めて書いた場合」の大きさを測る（2026-09-23 夜）。
ユーザー「**1秒か2秒くらい画面が暗くなる**」＝開くときの待ち。
何がどれだけ占めているかを数字で出す（[[project_index_html_size_ceiling]] の続き）。
使い方: python tmp/x0923/size_breakdown.py
"""
import io
import json
import os
import re

P = 'index.html'
raw = io.open(P, 'rb').read()
s = raw.decode('utf-8')
total = len(raw)

m = re.search(r'(  const EVENTS = )(\[)', s)
start = m.start(2)
events, end = json.JSONDecoder().raw_decode(s, start)
ev_bytes = len(s[start:end].encode('utf-8'))

# SSR（AIページ用に埋め込んだ静的HTML）
mssr = re.search(r'<!-- AI_SSR_START -->(.*?)<!-- AI_SSR_END -->', s, re.S)
ssr_bytes = len(mssr.group(1).encode('utf-8')) if mssr else 0

# 詰めて書いた場合
compact = json.dumps(events, ensure_ascii=False, separators=(',', ':'))
compact_bytes = len(compact.encode('utf-8'))

# 新着（まだ公開していい分ではない）を抜いた場合
pub = [e for e in events if e.get('genre') != 'new']
pub_compact = len(json.dumps(pub, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))

def mb(n):
    return '%.2f MB' % (n / 1024 / 1024)

lines = []
lines.append('index.html の内訳（%s・%d件）' % (mb(total), len(events)))
lines.append('  EVENTS配列      %s  （全体の %.0f%%）' % (mb(ev_bytes), ev_bytes * 100.0 / total))
lines.append('  SSR(AI_SSR)     %s' % mb(ssr_bytes))
lines.append('  それ以外        %s  （CSS・JS・HTMLの骨）' % mb(total - ev_bytes - ssr_bytes))
lines.append('')
lines.append('EVENTSを詰めて書いた場合（indentと空白を落とす）')
lines.append('  いま            %s' % mb(ev_bytes))
lines.append('  詰めると        %s   → 全体 %s（%s減）'
             % (mb(compact_bytes), mb(total - ev_bytes + compact_bytes), mb(ev_bytes - compact_bytes)))
lines.append('')
lines.append('さらに新着%d件を公開用から外した場合' % (len(events) - len(pub)))
lines.append('  EVENTS          %s   → 全体 %s（いまから %s減）'
             % (mb(pub_compact), mb(total - ev_bytes + pub_compact), mb(ev_bytes - pub_compact)))
lines.append('')
lines.append('※「画面が暗い1〜2秒」は ①ダウンロード ②JSONのパース ③初回描画 の合計。')
lines.append('  詰めるのは①にしか効かない（件数が変わらないので②はほぼ同じ）。')
lines.append('  ②③まで効かせるには「最初に見える分だけ読む」作りが要る。')

out = '\n'.join(lines) + '\n'
io.open('tmp/x0923/size_breakdown.txt', 'w', encoding='utf-8').write(out)
print(out)
