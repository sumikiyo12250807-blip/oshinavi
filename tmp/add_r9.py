# -*- coding: utf-8 -*-
"""2027年(令和9年=R9年)公演バッジに「R9年 」を付与。
判定: 公演月が1〜5月→2027(R9年)/6〜12月→2026(現在6月・過去の1-5月2026は買えないので確実)。
範囲 A〜B は端点ごとに年判定: 両方2027→「R9年 A〜B」/ 2026〜2027→「A〜R9年 B」。
（…公演）の中だけ処理し、販売日(〜M/D等)は触らない。既にR9年/令和9/2027年があるグループはskip。"""
import re, json, io, sys, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DRY = '--apply' not in sys.argv

def is2027(mo):  # 月→2027か
    return 1 <= mo <= 5

def proc_group(inner):
    """（…公演）の中身innerにR9年を挿入して返す。"""
    if 'R9年' in inner or '令和9' in inner or '2027年' in inner:
        return inner  # 既に年表記あり→触らない
    out = inner
    # まず範囲 A〜B を処理(プレースホルダ化して二重適用回避)
    def rep_range(m):
        m1, d1, m2, d2 = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
        a, b = f"{m1}/{d1}", f"{m2}/{d2}"
        if is2027(m1) and is2027(m2):
            return f"R9年 {a}〜{b}"
        if not is2027(m1) and is2027(m2):
            return f"{a}〜R9年 {b}"
        return f"{a}〜{b}"
    out = re.sub(r'(\d{1,2})/(\d{1,2})\s*〜\s*(\d{1,2})/(\d{1,2})', rep_range, out)
    # 次に単独 M/D (範囲で消費済みは〜を含むので、残る単独だけ)。R9年直後やレンジ内は除外。
    def rep_single(m):
        # 直前が "R9年 " か "〜" ならスキップ(範囲処理済)
        s = m.string; i = m.start()
        pre = s[max(0,i-5):i]
        if pre.endswith('R9年 ') or s[i-1:i] == '〜':
            return m.group(0)
        mo = int(m.group(1))
        return f"R9年 {m.group(0)}" if is2027(mo) else m.group(0)
    out = re.sub(r'(\d{1,2})/(\d{1,2})', rep_single, out)
    return out

def proc_type(ty):
    # 公演を含む（…）グループ全体を処理（複数公演キーワードも全部）。販売日は（）外なので無傷。
    return re.sub(r'（([^）]*公演[^）]*)）', lambda m: '（' + proc_group(m.group(1)) + '）', ty)

def has_2027(e):
    """このエントリが2027公演を含むか。公演月に1〜4月(Jan-Apr=2026は過去で確実に翌年)があるか
    ev.date>=2027なら2027持ち。5月単独・6〜12月だけ＝2026(id97/309/1400を除外)。"""
    if (e.get('date') or '') >= '2027-01-01':
        return True
    for t in e['tickets']:
        for grp in re.findall(r'（([^）]*公演[^）]*)）', t['type']):
            for mo, _ in re.findall(r'(\d{1,2})/(\d{1,2})', grp):
                if 1 <= int(mo) <= 4:
                    return True
    return False

h = open('index.html', encoding='utf-8').read()
m = re.search(r'const EVENTS = (\[.*?\]);', h, re.S)
arr = json.loads(m.group(1))
changes = []
for e in arr:
    if not has_2027(e):
        continue
    for t in e['tickets']:
        old = t['type']; new = proc_type(old)
        if new != old:
            changes.append((e['id'], e['name'][:24], old, new))
            t['type'] = new

print(f"=== R9年付与 変更 {len(changes)}件 ({'DRY-RUN' if DRY else '適用'}) ===")
for eid, nm, old, new in changes:
    print(f"\nid{eid} {nm}")
    print(f"  - {old}")
    print(f"  + {new}")

if not DRY and changes:
    new_block = json.dumps(arr, ensure_ascii=False, indent=2)
    new_txt = h[:m.start(1)] + new_block + h[m.end(1):]
    json.loads(re.search(r'const EVENTS = (\[.*?\]);', new_txt, re.S).group(1))
    shutil.copy('index.html', 'index.html.bak_0628_r9')
    open('index.html', 'w', encoding='utf-8').write(new_txt)
    print(f"\nWROTE index.html ({len(changes)}件) backup: index.html.bak_0628_r9")
