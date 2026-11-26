# -*- coding: utf-8 -*-
"""カンフェティ（confetti-web.com）の公演一覧と詳細ページを読む（2026-11-26 新設）。

🚨 渡部様（ロングランプランニング）との約束（11/25 の先方の希望・11/26 9時台の返信）を、道具の中で守る：
  - 1ページごとに10秒以上あける（この道具は12秒）
  - 同時に読むのは1本だけ（並べて走らせない＝鍵ファイル）
  - 詳細ページへは必ず一覧ページからたどる（その日に読んだ一覧に出てきた URL だけを開く・URL を作らない）
  - 読み込みの開始は毎日午前6時（6時より前は始めない・7時で必ず止める＝1回1時間以内）
  - 1日300ページまで（一覧＋詳細の合計・日ごとの帳面で数える）
  - 画像は読まない（Chrome の画像読み込みを切る）
  - 中止の依頼が来たら .claude/state/vendor_stop.json に "confetti" を書く＝何もせず終わる
  - 機械と見なされて断られた（403 など）ら、その日はそこで止める（すり抜ける工夫はしない＝先方に相談）

読むのは Chrome の画面なし（headless）。普通の読み込み（urllib）は 403 で断られるため。
生のページは公開のリポジトリに置かない（問い合わせ先のメールが入る）＝リポジトリの外 PRIV に置く。

  python tools/confetti_harvest.py            # 本番（6:00〜7:00 の間だけ動く）
  python tools/confetti_harvest.py --dry      # 売り場に行かずに、今日の帳面と次に読む予定だけ出す

出力：PRIV/YYYYMMDD/list_NN.html・detail_<番号>.html、PRIV/ledger.json（読んだ詳細と一覧の見出し）、
      PRIV/YYYYMMDD/log.txt。組み立て（build_confetti_entries）は別の道具。
"""
import argparse
import datetime as dt
import io
import json
import os
import re
import subprocess
import sys
import time
from urllib.parse import urljoin, urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vendor_stop  # noqa: E402
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRIV = os.path.join(os.path.dirname(ROOT), 'oshinavi_private', 'confetti')
HOST = 'www.confetti-web.com'
LIST_URL = 'https://www.confetti-web.com/events'
GAP = 12            # 秒（約束は10秒以上）
DAY_MAX = 300       # 1日のページ数の上限
START = dt.time(6, 0)
STOP = dt.time(7, 0)
CHROME = [r'C:\Program Files\Google\Chrome\Application\chrome.exe',
          r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe']
LOCK = os.path.join(PRIV, 'run.lock')
# 詳細ページの形（一覧の中のリンクから拾う・この形に合わないリンクは開かない）
DETAIL_RE = re.compile(r'^/events/(\d+)/?$')


class Blocked(Exception):
    pass


def now():
    return dt.datetime.now()


def log(day_dir, m):
    s = now().strftime('%H:%M:%S ') + m
    try:
        print(s)
    except Exception:
        pass
    io.open(os.path.join(day_dir, 'log.txt'), 'a', encoding='utf-8').write(s + '\n')


def load_ledger():
    p = os.path.join(PRIV, 'ledger.json')
    try:
        return json.load(io.open(p, encoding='utf-8'))
    except Exception:
        return {'pages': {}, 'detail': {}, 'listsig': {}}


def save_ledger(L):
    p = os.path.join(PRIV, 'ledger.json')
    io.open(p + '.tmp', 'w', encoding='utf-8').write(json.dumps(L, ensure_ascii=False, indent=1))
    os.replace(p + '.tmp', p)


class Reader:
    """1ページずつ・12秒あけ・上限・時刻を守って読む。"""

    def __init__(self, L, day, day_dir):
        self.L, self.day, self.dir = L, day, day_dir
        self.last = 0.0
        self.profile = os.path.join(PRIV, 'chrome_profile')
        self.chrome = next(p for p in CHROME if os.path.exists(p))

    def used(self):
        return self.L['pages'].get(self.day, 0)

    def can(self):
        if self.used() >= DAY_MAX:
            return '1日の上限 %d ページ' % DAY_MAX
        if now().time() >= STOP:
            return '7時になった（1回1時間以内）'
        return ''

    def get(self, url):
        why = self.can()
        if why:
            raise StopIteration(why)
        u = urlparse(url)
        if u.netloc != HOST:
            raise ValueError('カンフェティ以外は開かない: ' + url)
        wait = self.last + GAP - time.time()
        if wait > 0:
            time.sleep(wait)
        vendor_stop.check('confetti')   # 途中で中止の札が立ったらすぐ止める
        cmd = [self.chrome, '--headless=new', '--disable-gpu', '--no-first-run',
               '--no-default-browser-check', '--user-data-dir=' + self.profile,
               '--blink-settings=imagesEnabled=false', '--virtual-time-budget=8000',
               '--dump-dom', url]
        r = subprocess.run(cmd, capture_output=True, timeout=90)
        self.last = time.time()
        self.L['pages'][self.day] = self.used() + 1
        save_ledger(self.L)
        html = r.stdout.decode('utf-8', 'replace')
        low = html.lower()
        if len(html) < 2000 or 'access denied' in low or '403 forbidden' in low or 'request blocked' in low:
            raise Blocked('断られた形（長さ %d）: %s' % (len(html), url))
        # 🆕11/27 初回＝Cloudflare の確かめの画面（題「しばらくお待ちください...」・cloudflare へのリンクだけ）が返った
        #   ＝bot 判定で止められた形。すり抜けない（待って読み直す・UA を替えるなどはしない）＝その日止めて先方に相談
        if 'しばらくお待ちください' in html or 'just a moment' in low or 'challenge-platform' in low or 'cf-chl' in low:
            raise Blocked('断られた形（Cloudflare の確かめの画面・長さ %d）: %s' % (len(html), url))
        return html


def links(html, base):
    out = []
    for m in re.finditer(r'<a\b[^>]*?href="([^"#]+)"', html):
        h = m.group(1).replace('&amp;', '&')
        u = urljoin(base, h)
        if urlparse(u).netloc == HOST:
            out.append(u)
    return out


def detail_urls(html, base):
    seen, out = set(), []
    for u in links(html, base):
        p = urlparse(u)
        m = DETAIL_RE.match(p.path)
        if m and m.group(1) not in seen:
            seen.add(m.group(1))
            out.append((m.group(1), 'https://%s%s' % (HOST, p.path.rstrip('/'))))
    return out


def next_list(html, base, cur_n):
    """一覧の「次のページ」を、ページの中のリンクから拾う（URL を作らない）。"""
    want = cur_n + 1
    for u in links(html, base):
        p = urlparse(u)
        if p.path.rstrip('/') != '/events':
            continue
        m = re.search(r'(?:^|&)page=(\d+)', p.query)
        if m and int(m.group(1)) == want:
            return u
    return None


def item_sig(html, eid):
    """一覧の中で、その公演のリンクのまわりの文字（発売の状況が変わったかを見る）。"""
    i = html.find('/events/%s"' % eid)
    if i < 0:
        return ''
    seg = html[max(0, i - 200): i + 1500]
    seg = re.sub(r'<[^>]+>', ' ', seg)
    return re.sub(r'\s+', ' ', seg).strip()[:600]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry', action='store_true')
    a = ap.parse_args()
    vendor_stop.check('confetti')
    day = now().strftime('%Y%m%d')
    day_dir = os.path.join(PRIV, day)
    os.makedirs(day_dir, exist_ok=True)
    L = load_ledger()
    if a.dry:
        print('今日読んだページ', L['pages'].get(day, 0), '/', DAY_MAX)
        print('読んだ詳細', len(L['detail']), '｜一覧で覚えている公演', len(L['listsig']))
        return
    t = now().time()
    if not (START <= t < STOP):
        print('🚫 いまは %s＝6:00〜7:00 の外なので読まない（約束：開始は午前6時・1回1時間以内）' % t.strftime('%H:%M'))
        return
    try:
        fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
    except FileExistsError:
        print('🚫 もう1本動いている（同時に1本だけ）:', LOCK)
        return
    R = Reader(L, day, day_dir)
    stop_why = ''
    try:
        # 1) 一覧を1ページ目から、ページの中の「次」のリンクでたどる
        found = []   # (eid, url, sig)
        url, n = LIST_URL, 1
        while url:
            html = R.get(url)
            io.open(os.path.join(day_dir, 'list_%02d.html' % n), 'w', encoding='utf-8').write(html)
            d = detail_urls(html, url)
            for eid, du in d:
                found.append((eid, du, item_sig(html, eid)))
            log(day_dir, '一覧 %d ページ目：公演 %d（今日 %d ページ目）' % (n, len(d), R.used()))
            if not d:
                stop_why = '一覧から詳細のリンクが1つも拾えない＝ページの形が想定と違う（DETAIL_RE を直す）'
                break
            url = next_list(html, url, n)
            n += 1
        if not stop_why:
            log(day_dir, '一覧おわり %d ページ・公演 %d' % (n - 1, len(found)))
        # 2) 詳細：まだ読んでいない公演 → 一覧の文字が前と変わった公演、の順（一覧に出た URL だけ）
        todo_new = [f for f in found if f[0] not in L['detail']]
        todo_chg = [f for f in found if f[0] in L['detail'] and L['listsig'].get(f[0]) != f[2]]
        log(day_dir, '詳細の予定：まだ読んでいない %d・一覧の文字が変わった %d' % (len(todo_new), len(todo_chg)))
        for eid, du, sig in todo_new + todo_chg:
            html = R.get(du)
            io.open(os.path.join(day_dir, 'detail_%s.html' % eid), 'w', encoding='utf-8').write(html)
            L['detail'][eid] = {'url': du, 'day': day}
            L['listsig'][eid] = sig
            save_ledger(L)
        # 一覧に出たが今日は上限で読めなかった分は listsig を更新しない＝明日また候補に出る
    except StopIteration as e:
        stop_why = str(e)
    except Blocked as e:
        stop_why = '🚨 ' + str(e) + '＝今日はここで止める（すり抜けない・渡部様に相談）'
    finally:
        try:
            os.remove(LOCK)
        except OSError:
            pass
        save_ledger(L)
        log(day_dir, 'おわり：今日 %d ページ・読んだ詳細の合計 %d%s' % (
            L['pages'].get(day, 0), len(L['detail']), ('｜止めたわけ：' + stop_why) if stop_why else ''))


if __name__ == '__main__':
    main()
