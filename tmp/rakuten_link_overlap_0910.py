# -*- coding: utf-8 -*-
"""「楽天でも買えるのに楽天リンクが無い」エントリに、楽天リンクと楽天の枠を入れる。

  python tmp/rakuten_link_overlap_0910.py            … 調べるだけ
  python tmp/rakuten_link_overlap_0910.py --apply

ユーザー（2026-09-10）＝「ぴあのリンクは0円だけど楽天チケットはアフィリあるから…
できるだけ楽天貼って頂戴」。

🚨ただし決まり（[[feedback_vendor_priority]]）＝
  「そこで売っていないのに楽天リンクを貼らない。優先順位は**探す順番**であって
   **無理やり埋める順番**ではない」。
  → だから**実ページから枠を作り直して、公演日が既存と重なるものだけ**を対象にする。
  → ぴあの締切を出したまま楽天へ飛ばすのは禁止（今日1日かけて消した「嘘の締切」を作り直すことになる）。

やること:
 1. 楽天の実ページから枠を作る（build_rakuten_entries＝締切も売り状態も楽天の事実）
 2. **公演日が既存エントリと1つでも重なる**ことを確かめる（別公演に貼らない安全弁）
 3. links.rakuten を入れる（Deep Link）
 4. 楽天の枠を足す（（県・公演日・締切）で突き合わせ＝券種名だと二重登録になる）
"""
import io
import json
import re
import sys
import time
import urllib.parse

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_harvest as RH
import build_rakuten_entries as B

APPLY = '--apply' in sys.argv


def raw_url(u):
    m = re.search(r'murl=([^&]+)', u or '')
    return urllib.parse.unquote(m.group(1)) if m else (u or '')


def slot_key(t):
    m = re.search(r'（([^（）]*?)\s*((?:R\d+年\s*)?[\d/〜]+)(?:\s+\d{1,2}:\d{2})?公演）', t.get('type') or '')
    if not m:
        return (t.get('type'), '', t.get('date'))
    return (m.group(1).strip(), re.sub(r'R\d+年\s*', '', m.group(2)).strip(), t.get('date'))


def perf_days(e):
    """エントリが名乗っている公演日（M/D）の集合。バッジから取る。"""
    out = set()
    for t in e.get('tickets') or []:
        m = re.search(r'（[^（）]*?((?:R\d+年\s*)?\d{1,2}/\d{1,2}(?:〜(?:R\d+年\s*)?\d{1,2}/\d{1,2})?)',
                      t.get('type') or '')
        if m:
            for x in m.group(1).split('〜'):
                out.add(re.sub(r'^R\d+年\s*', '', x.strip()))
    return out


src = io.open('index.html', encoding='utf-8').read()
mm = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(mm.group(2))
by = {e['id']: e for e in events}

pairs = json.load(io.open('tmp/rakuten_link_pairs_0910.json', encoding='utf-8'))

linked = added = 0
skipped = []
for p in pairs:
    e = by.get(p['id'])
    if not e:
        continue
    u = p['url']
    try:
        rec = RH.parse_page(u, RH.fetch(u))
    except Exception as ex:
        skipped.append((p['id'], u, '取得失敗 %r' % (ex,)))
        continue
    ne, why = B.build([rec], e['id'])
    if not ne:
        skipped.append((p['id'], u, '枠が作れない（%s）' % why))
        continue

    # 🚨安全弁＝公演日が1つも重ならないなら**別の公演**。貼らない
    mine, theirs = perf_days(e), perf_days(ne)
    if not (mine & theirs):
        skipped.append((p['id'], u, '公演日が1つも重ならない（別公演の疑い）'))
        continue

    # 🚨🚨links.rakuten を足す**前に**、url が空の枠へ今の飛び先を焼き込む。
    #   画面は ticketLinkUrl = links.rakuten || links.pia || … の順で決めるので、
    #   楽天リンクを足した瞬間に**ぴあの枠まで楽天へ飛ぶ**ようになる。
    #   ぴあと楽天は販売枠が別なので、これは「買えない窓へ誘導する」＝嘘になる。
    burned_here = 0
    if not (e.get('links') or {}).get('rakuten'):
        cur_default = ((e.get('links') or {}).get('pia')
                       or (e.get('links') or {}).get('eplus')
                       or (e.get('links') or {}).get('lawson'))
        for t in e.get('tickets') or []:
            if not t.get('url') and cur_default:
                t['url'] = cur_default
                burned_here += 1
        e.setdefault('links', {})['rakuten'] = B.deeplink(u)
        linked += 1
    have = {slot_key(t) for t in (e.get('tickets') or [])}
    news = [t for t in ne['tickets'] if slot_key(t) not in have]
    e.setdefault('tickets', []).extend(news)
    added += len(news)
    print('🎫 id=%-5s %-34s ＋%d枠 / 既存の飛び先を焼き込み %d枠  重なる公演日 %s'
          % (e['id'], (e.get('name') or '')[:34], len(news), burned_here,
             '/'.join(sorted(mine & theirs))[:30]))
    for t in news:
        print('        %s' % t['type'][:70])
    time.sleep(0.4)

print('\n楽天リンクを入れた %d件 / 足した枠 %d / 貼らなかった %d件' % (linked, added, len(skipped)))
for i, u, why in skipped:
    print('  ⏭️ id=%-5s %s … %s' % (i, why, u))

if not APPLY:
    print('\n(--apply で書き込み)')
    sys.exit(0)
arr = json.dumps(events, ensure_ascii=False, indent=2)
io.open('index.html', 'w', encoding='utf-8').write(
    src[:mm.start()] + mm.group(1) + arr + mm.group(3) + src[mm.end():])
print('書き込み完了')
