# -*- coding: utf-8 -*-
"""reconcile_rakuten.py に「新型（data-event-json）」の読み方を足す。

【穴】ハーベスタは 2026-09-08 に新型を読めるようにしたが、**照合ツールは従来型しか見ていない**。
     結果、今日投入した新型3件（THE ORCHESTRA TOKYO／Chalca／ちゃーむぽっしゅ）が
     「照合対象外」になった＝**入口は硬いのに出口が見ていない**。
     これは [[project_rakuten_make_it_ironclad]] の「入口だけ硬くしても鉄壁にならない」そのもの。

【直し】perfs も windows も0件だった時だけ parse_event_json を辿る。
     ハーベスタ本体と**同じ順番・同じ条件**にそろえる（片方だけ賢いと今回のズレがまた起きる）。
"""
import io

P = "tools/reconcile_rakuten.py"
s = io.open(P, encoding="utf-8").read()

old = """            perfs += R.parse_perfs(b)
            wins += R.parse_windows(b)"""
new = """            p1, w1 = R.parse_perfs(b), R.parse_windows(b)
            if not p1 and not w1:
                # 🆕新型＝HTMLは空の型だけで data-event-json が指す外部JSONに中身がある。
                #   ハーベスタ側と同じ条件で辿る（入口だけ読めて出口が読めないと照合が抜ける）。
                ej = R.parse_event_json(b)
                if ej:
                    p1, w1 = ej.get('perfs') or [], ej.get('windows') or []
            perfs += p1
            wins += w1"""
assert s.count(old) == 1
s = s.replace(old, new, 1)

io.open(P, "w", encoding="utf-8").write(s)
print("reconcile_rakuten.py に新型の読み方を足した")
