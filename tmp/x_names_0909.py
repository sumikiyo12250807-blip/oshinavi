# -*- coding: utf-8 -*-
"""予約した12本の本文から、総ざらい対象のアーティスト/公演名を抜き出す。
   🚨ぴあのツアーまとめページだけ見ない＝アーティスト名で検索する
      （feedback_pia_bundle_hides_shows）"""
import io, re, sys, json
sys.stdout.reconfigure(encoding="utf-8")

names = []
for i in range(1, 13):
    p = io.open("tmp/posts0909/%02d.txt" % i, encoding="utf-8").read()
    # 【9/9(水)発売】ブロックの「HH:MM 名前／県」行から名前を取る
    for m in re.finditer(r"^\d{2}:\d{2}\s+(.+?)／", p, re.M):
        nm = m.group(1).strip()
        nm = re.sub(r"\s+\d{4}$", "", nm)          # 「こおり健太 2026」→ こおり健太
        nm = re.sub(r"\s+\d{1,2}/\d{1,2}.*$", "", nm)
        if nm not in names:
            names.append(nm)

io.open("tmp/x_names_0909.json", "w", encoding="utf-8").write(
    json.dumps(names, ensure_ascii=False, indent=1))
print("総ざらい対象 %d件" % len(names))
for n in names:
    print(" ", n)
