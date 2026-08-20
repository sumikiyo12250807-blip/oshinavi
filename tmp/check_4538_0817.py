# -*- coding: utf-8 -*-
"""dedup_badges が 4538 を 7→3 に畳んだのは正しいか。
畳む前（バックアップ）と今を並べて、落ちた4枠が「表示が完全に同じ重複」だったのか、
それとも別物（＝買える枠を1つ落とした）のかを見る。"""
import io, re, sys, json
sys.stdout.reconfigure(encoding='utf-8')


def load(path):
    s = io.open(path, encoding='utf-8').read()
    return {e['id']: e for e in json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', s, re.S).group(2))}


now = load('index.html')[4538]
before = load('index.html.bak_0817_dedup_badges')[4538]

print('=== 畳む前 %d枠 ===' % len(before.get('tickets') or []))
for t in before['tickets']:
    print('  type=%s' % t.get('type'))
    print('     start=%s date=%s badge=%s url=%s'
          % (t.get('startDate'), t.get('date'), t.get('badge', ''), (t.get('url') or '')[:70]))

print()
print('=== 畳んだ後 %d枠 ===' % len(now.get('tickets') or []))
for t in now['tickets']:
    print('  type=%s' % t.get('type'))
    print('     start=%s date=%s url=%s' % (t.get('startDate'), t.get('date'), (t.get('url') or '')[:70]))

print()
lost = [t for t in before['tickets'] if t not in now['tickets']]
print('=== 落ちた %d枠（URLまで含めて比較）===' % len(lost))
for t in lost:
    print('  %s | %s〜%s | %s' % (t.get('type'), t.get('startDate'), t.get('date'), t.get('url')))

print()
urls_b = {t.get('url') for t in before['tickets']}
urls_n = {t.get('url') for t in now['tickets']}
print('URLの数 畳む前 %d → 後 %d' % (len(urls_b), len(urls_n)))
print('消えたURL:', urls_b - urls_n or 'なし')
