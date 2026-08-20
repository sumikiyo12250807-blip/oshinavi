# -*- coding: utf-8 -*-
"""SOLD疑い(未来公演0枚)の生HTML診断。各ぴあページのticketSalesCard状態テキストを直接列挙。"""
import re, json, io, sys, time, importlib.util
spec = importlib.util.spec_from_file_location('bpe', 'tools/build_pia_entries.py')
bpe = importlib.util.module_from_spec(spec); spec.loader.exec_module(bpe)  # bpeがstdoutをUTF-8ラップ

d = json.load(open('tmp/convert_0628.json', encoding='utf-8'))
SUS = [43,147,273,417,493,604,648,743,760,881,1033,1034,1329]

for eid in SUS:
    r = d[str(eid)]
    print(f"\n===== id{eid} {r['name'][:36]} | 公演:{r['perf_date']} =====")
    for u in r['urls']:
        try:
            h = bpe.fetch(u)
            cards = re.split(r'(?=<li class="ticketSalesList-2024__item)', h)
            ncards = sum(1 for c in cards if 'ticketSalesCard-2024__status' in c)
            # 状態テキスト抽出
            stats = re.findall(r'__status (is-[\w-]+)">(.*?)(?:<br|</p>)', h, re.S)
            sorry = '予定枚数' in h or '販売を終了' in h or 'ご用意のチケットは' in h
            print(f"  URL末尾 ...{u[-24:]} | cards={ncards} | 'sorry/枚数'語={sorry}")
            for cls, txt in stats[:12]:
                print(f"     [{cls}] {bpe.txt(txt)[:40]}")
        except Exception as ex:
            print(f"  URL {u[-24:]} ERR {ex}")
        time.sleep(0.3)
