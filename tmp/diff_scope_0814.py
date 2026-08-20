# -*- coding: utf-8 -*-
"""index.html の変更がSSR/件数/更新スタンプだけで、EVENTS本体は無傷か検算。"""
import re, sys, hashlib
sys.stdout.reconfigure(encoding='utf-8')

def events_blob(path):
    h = open(path, encoding='utf-8', newline='').read()
    return re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2), h

new, hn = events_blob('index.html')
old, ho = events_blob('index.html.bak_0814_ssr_soldout')
print('EVENTS 同一?', hashlib.sha256(new.encode()).hexdigest() == hashlib.sha256(old.encode()).hexdigest())
print('EVENTS 長さ', len(old), '→', len(new))

def outside(h):
    """SSRブロックと件数・更新スタンプを除いた残り"""
    h = re.sub(r'<!-- AI_SSR_START -->.*?<!-- AI_SSR_END -->', 'SSR', h, flags=re.S)
    h = re.sub(r'(<span id="resultCount">)\d+(</span>)', r'\1N\2', h)
    h = re.sub(r'(<span class="lu-stamp" id="lastUpdated">).*?(</span>)', r'\1S\2', h, flags=re.S)
    return h

print('SSR/件数/スタンプ以外は同一?', outside(ho) == outside(hn))
