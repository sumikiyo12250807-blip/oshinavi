# -*- coding: utf-8 -*-
"""reconcile_rakuten.py の誤検知を2つ塞ぐ（2026-09-08 実測で発見）。

【穴①】楽天でない枠まで楽天のページと突き合わせていた
  id3514 BERITA は **枠3つとも ticket.pia.jp** で、楽天はカードの買うボタンだけ。
  それを楽天のページと照合して「締切がページに無い」とFAILにしていた。
  → **枠の url が楽天のものだけ照合する**。判定できない枠は 未照合 に数える。
     （[[feedback_delete_nonpia_blindspot]]の裏返し＝売り手ごとに照合する道具を混ぜない）

【穴②】もう終わった日を「ページに無い」と鳴らしていた
  id3228 尾上右近は「9/5〜10/3公演」で、9/5 は既に終わっている＝楽天のページから消える。
  id3224 MATSURI も同じで「8/8〜12/6公演」の 8/8 が消えている。
  ラベルは**事実の会期**を書く決まりなので、これは登録が正しくてページが減っただけ
  （[[feedback_show_true_dates_not_sellable_range]]）。
  → **今日より前の日付は FAIL にせず 未照合 として数える**。
"""
import io

P = "tools/reconcile_rakuten.py"
s = io.open(P, encoding="utf-8").read()

# ---- ① 楽天の枠だけを見る判定を足す -------------------------------------
old_head = '''def raw_url(u):'''
new_head = '''RAKUTEN_URL = re.compile(r'ticket\\.rakuten\\.co\\.jp|linksynergy\\.com/deeplink')


def rakuten_slot(e, t):
    """この枠を楽天のページと突き合わせてよいか。

    🚨楽天リンクを持つエントリでも、枠そのものはぴあ/e+のことがある（買うボタンだけ楽天）。
      それを楽天のページと照合すると必ず外れる＝本物のFAILが埋もれる。
      url が楽天なら見る。url が空の枠は、そのエントリに**他社リンクが1つも無い時だけ**見る。
    """
    u = t.get('url') or ''
    if u:
        return bool(RAKUTEN_URL.search(u))
    ls = e.get('links') or {}
    return not any(ls.get(k) for k in ('pia', 'eplus', 'lawson'))


def past(d):
    """今日より前＝楽天のページからは消えている。照合できないだけで、登録が誤りとは限らない。"""
    return bool(d) and d[:10] < TODAY


def raw_url(u):'''
assert s.count(old_head) == 1
s = s.replace(old_head, new_head, 1)

# ---- 枠ループの入口で振り分ける -----------------------------------------
old_loop = """        for t in e.get('tickets', []):
            checked = False
            # ① 締切（公演日で締めた/売り切れ次第終了は照合対象外＝skip）"""
new_loop = """        for t in e.get('tickets', []):
            checked = False
            if not rakuten_slot(e, t):
                skip_slots += 1      # 🚨楽天の枠でない＝この道具の担当外（黙って合格にしない）
                continue
            # ① 締切（公演日で締めた/売り切れ次第終了は照合対象外＝skip）"""
assert s.count(old_loop) == 1
s = s.replace(old_loop, new_loop, 1)

# ---- ② 過ぎた締切をFAILにしない -----------------------------------------
old_end = """                if '%d/%d' % (int(t['date'][5:7]), int(t['date'][8:10])) in page_perf_md:
                    checked = True
                else:
                    errs.append('締切 %s がページに無い | %s' % (t['date'], t['type'][:34]))"""
new_end = """                if '%d/%d' % (int(t['date'][5:7]), int(t['date'][8:10])) in page_perf_md:
                    checked = True
                elif past(t['date']):
                    pass             # 🚨終わった枠はページから消える＝照合できないだけ
                else:
                    errs.append('締切 %s がページに無い | %s' % (t['date'], t['type'][:34]))"""
assert s.count(old_end) == 1
s = s.replace(old_end, new_end, 1)

old_start = """                if t['startDate'] in page_start:
                    checked = True
                else:
                    errs.append('発売日 %s がページに無い | %s' % (t['startDate'], t['type'][:34]))"""
new_start = """                if t['startDate'] in page_start:
                    checked = True
                elif past(t['startDate']):
                    pass             # 🚨発売済みの先行はページの販売枠から落ちる
                else:
                    errs.append('発売日 %s がページに無い | %s' % (t['startDate'], t['type'][:34]))"""
assert s.count(old_start) == 1
s = s.replace(old_start, new_start, 1)

# ---- ③ 過ぎたバッジ公演日をFAILにしない ---------------------------------
old_badge = """                for one in badge.group(1).split('〜'):
                    if one and one not in page_perf_md:
                        errs.append('バッジ公演日 %s がページに無い | %s' % (one, t['type'][:34]))
                    else:
                        checked = True"""
new_badge = """                for one in badge.group(1).split('〜'):
                    if not one:
                        continue
                    if one in page_perf_md:
                        checked = True
                        continue
                    # 🚨ラベルは「事実の会期」を書く決まりなので、初日が過ぎたツアーは
                    #   ページ側だけが減る。これを鳴らすと毎回FAILになって本物が埋もれる。
                    mo, dy = (int(x) for x in one.split('/'))
                    yr = int(TODAY[:4]) + (1 if mo < int(TODAY[5:7]) - 6 else 0)
                    if '%04d-%02d-%02d' % (yr, mo, dy) < TODAY:
                        continue
                    errs.append('バッジ公演日 %s がページに無い | %s' % (one, t['type'][:34]))"""
assert s.count(old_badge) == 1
s = s.replace(old_badge, new_badge, 1)

io.open(P, "w", encoding="utf-8").write(s)
print("reconcile_rakuten.py を直した（楽天の枠だけ照合／過ぎた日はFAILにしない）")
