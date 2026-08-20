# -*- coding: utf-8 -*-
"""ぴあkw検索の結果から「発売前 / 一般発売 / 受付中」の生きている枠だけ抜き出す。"""
import re, glob, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
NAME = {1554:'高嶋ちさ子',1601:'藍井エイル',2748:'熊本地震10年復興',3473:'AA=',3509:'田辺花火大会',
3696:'Stray Kids',4035:'紫 今',4036:'Little Parade',4050:'Bray me',4051:'K-Drama OST',
4057:'Faulieu.',4066:'新サクラ大戦',4080:'澤野弘之ガンダム',4081:'梅田サイファー',4083:'汐れいら',
4089:'花宮初奈',4094:'KAWAII LAB.',4098:'高木いくの',4100:'Khalid',4106:'徹子の部屋',
4114:'Yung Kai',4115:'THE MACKSHOW',4117:'RAINCOVER',4150:'FIVE O ONE',4156:'IRIS MONDO',
4159:'わーすた',4163:'中本こまり',4165:'TAKERU',4167:'Ken Yokoyama',4172:'Bocchi',
4175:'THE PREDATORS',4422:'yeti let you notice',4423:'The Performance Zero',4424:'シャッポ',4425:'スミワタルトリオ'}
for f in sorted(glob.glob('tmp/zbkw/*.txt'), key=lambda p:int(os.path.basename(p)[:-4])):
    eid = int(os.path.basename(f)[:-4])
    d = open(f, encoding='utf-8').read()
    blocks = re.split(r'\n(?=\[)', d)
    live = []
    for b in blocks:
        if not b.startswith('['): continue
        st = b[1:b.index(']')]
        if st in ('受付終了','販売終了','予定枚数終了'): continue
        live.append(b.strip())
    print('='*66)
    print('### id=%d %s  … 生き枠 %d件' % (eid, NAME.get(eid,''), len(live)))
    for b in live:
        print('  ' + b.replace('\n', '\n  ')[:600])
