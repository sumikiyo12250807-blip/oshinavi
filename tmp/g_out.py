# -*- coding: utf-8 -*-
import json, os
BASE = r"C:/Users/user/oshinavi"
ext = json.load(open(os.path.join(BASE, "tmp/g_extract.json"), encoding="utf-8"))
items = json.load(open(os.path.join(BASE, "tmp/genre_in_0825.json"), encoding="utf-8"))

CDSUB = {"0100102": u"音楽/J-POP・ROCK", "0100108": u"音楽/海外ROCK・POPS"}

D = {
"5097": ("jpop", u"高", u""),
"5098": ("jpop", u"低", u"ぴあ=音楽/音楽その他。実体はマーチングバンド（吹奏楽）の東京都大会＝関東大会予選。受け皿ルールでjpopにしたが、吹奏楽の大会をJ-POPタブに置くのは違和感がある。classic寄りに置く選択肢もあり要相談。"),
"5099": ("dento", u"高", u""),
"5100": ("kids", u"中", u"ぴあ=イベント/子供と楽しむ→kids。ただし名称は「ファミリーミュージカル」でmusicalにも掛かる。サンリオキャラ目当ての親子連れが主客なのでkidsを主にした。"),
"5101": ("owarai", u"高", u""),
"5102": ("dento", u"高", u""),
"5103": ("classic", u"高", u""),
"5104": ("classic", u"高", u""),
"5105": ("classic", u"高", u""),
"5106": ("classic", u"高", u""),
"5107": ("classic", u"高", u""),
"5111": ("kids", u"高", u""),
"5112": ("dinnershow", u"高", u""),
"5113": ("art", u"高", u""),
"5114": ("classic", u"高", u""),
"5115": ("classic", u"高", u""),
"5116": ("classic", u"高", u""),
"5117": ("classic", u"高", u""),
"5118": ("classic", u"高", u""),
"5119": ("enka", u"低", u"ぴあ=イベント/イベントその他（対応表に無い区分）。内容は「生バンド演奏で杉良太郎が魂の歌唱」＋講演、すきま風発売50周年。主役は歌謡・演歌の歌手なのでenkaにしたが、講演会（engeki）やfaneventとも読める。"),
"5120": ("gourmet", u"低", u"ぴあ=イベント/イベントその他（対応表に無い区分）。NPO法人プロフェッショナル・バーテンダーズ機構主催のカクテル＆バーの催し（20歳未満入場不可・ホテル宴会場）。飲食の催しなのでgourmetにしたが、ぴあの区分からは決められなかった。"),
"5121": ("kids", u"高", u""),
"5122": ("gourmet", u"低", u"ぴあ=イベント/スクール・レジャー→対応表ではkidsだが、実体は十勝若牛のバーベキューセット引換券＝フードフェスティバル。kidsタブに出すのは明らかにずれるのでgourmetにした。対応表を優先するならkids。"),
"5123": ("sports", u"高", u""),
"5124": ("jpop", u"高", u"bundleのためtitleに区分が出ない。隠しinput genreCd=0100102（音楽/J-POP・ROCK）で確定。"),
"5125": ("jpop", u"中", u"ぴあ=音楽/J-POP・ROCK。会場がザ・シンフォニーホールでクラシック系にも見えるが、ぴあの区分どおりjpop。"),
"5126": ("jpop", u"高", u"ジャズ寄りのピアノトリオだが、ぴあの区分が音楽/J-POP・ROCKなのでそのまま写した。"),
"5127": ("jpop", u"低", u"ぴあ=音楽/音楽その他→受け皿でjpop。実体は日経ミューズサロン第577回、竹内永和のクラシックギター＋榎木孝明。classicに置くほうがファンの探し方に合う可能性が高い。"),
"5128": ("jpop", u"高", u""),
"5130": ("jpop", u"高", u"bundle。genreCd=0100102で確定。"),
"5131": ("jpop", u"低", u"ぴあ=音楽/音楽その他→受け皿でjpop。紹介文は「洋楽器と和楽器が織りなす」＝和楽器が入る編成。dentoにも掛かるが、ぴあのサブが演歌・邦楽ではないのでdento条件は適用しなかった。"),
"5132": ("dento", u"高", u"ぴあ=音楽/演歌・邦楽。公演名の副題が「第二十五回 音輪会雅楽演奏会」＝雅楽なのでdento（enkaではない）。"),
"5133": ("yougaku", u"高", u"bundle。genreCd=0100108（音楽/海外ROCK・POPS）。EVANESCENCEは米国のバンドで韓国ではないのでyougaku。"),
"5135": ("jpop", u"高", u""),
"5136": ("jpop", u"高", u""),
"5139": ("kpop", u"高", u"ぴあ=音楽/海外ROCK・POPSだが、wave to earthは韓国ソウルのバンド。ぴあ自身がページに「K-POP・韓流エンタメ」タグを付けているのでkpop。"),
"5141": ("jpop", u"高", u""),
"5142": ("jpop", u"高", u""),
"5143": ("jpop", u"中", u"ぴあ=音楽/J-POP・ROCK。実体はシンガーソングライターLioraの実話をもとにした「アニメ・ソロミュージカル」でmusicalにも掛かるが、主役は歌手なのでjpop。"),
"5144": ("yougaku", u"高", u"bundle。genreCd=0100108。WOLF ALICEは英国のバンドで韓国ではないのでyougaku。"),
"5146": ("jpop", u"高", u""),
"5147": ("jpop", u"高", u""),
"5148": ("jpop", u"高", u""),
"5151": ("jpop", u"高", u""),
"5152": ("jpop", u"高", u""),
"5153": ("jpop", u"高", u"アイドルだが対応表どおりidolに細分せずjpop。"),
"5154": ("jpop", u"高", u""),
"5155": ("jpop", u"高", u"bundle。genreCd=0100102で確定。"),
"5156": ("jpop", u"中", u"ぴあ=音楽/フェスティバル。出演はENTH/envy/FIVE STATE DRIVE/KUZIRA/SHANK/TIVE/花冷え。＝複数組だが、会場がAichi Sky Expo（愛知国際展示場）展示ホールA〜D＝屋内。fesの定義「複数組＋屋外」を満たさないのでjpop。"),
"5157": ("jpop", u"高", u"対バンライブ（go!go!vanillas／ハンブレッダーズ）だが屋内ライブハウス規模でfesではない。"),
"5158": ("jpop", u"高", u"bundle。genreCd=0100102で確定。"),
"5159": ("jpop", u"高", u""),
"5160": ("jpop", u"高", u""),
"5161": ("jpop", u"高", u""),
"5162": ("jpop", u"高", u""),
"5164": ("classic", u"高", u""),
"5165": ("classic", u"高", u""),
"5166": ("classic", u"高", u""),
"5167": ("classic", u"高", u""),
"5168": ("classic", u"高", u""),
"5169": ("classic", u"高", u""),
"5170": ("classic", u"高", u""),
"5171": ("classic", u"高", u""),
"5172": ("classic", u"中", u"ぴあ=クラシック/クラシックその他→classic。実体は「ドイツ歌曲の森 vol.2 入門講座 第3回」＝演奏会でなく講座。イベント/講演会ならengekiになる区分だが、ぴあがクラシックに置いているのでclassicのまま。"),
"5173": ("classic", u"高", u""),
"5174": ("classic", u"高", u""),
"5175": ("classic", u"高", u""),
"5176": ("classic", u"高", u""),
"5177": ("classic", u"高", u"ぴあタグは「映画音楽・シネマコンサート」だがサブジャンルはクラシック/オーケストラなのでclassic。"),
"5178": ("classic", u"高", u""),
"5179": ("dento", u"高", u""),
"5180": ("owarai", u"高", u"ATSUKO OKATSUKAは日系アメリカ人のスタンダップコメディアン。ぴあ=演劇/寄席・お笑いでowarai。"),
"5181": ("musical", u"高", u""),
"5182": ("owarai", u"高", u"浪曲だが、ぴあの区分が演劇/寄席・お笑いなのでowarai。"),
"5184": ("owarai", u"高", u"講談だが、ぴあの区分が演劇/寄席・お笑いなのでowarai。"),
"5185": ("owarai", u"高", u""),
"5187": ("owarai", u"高", u""),
"5188": ("owarai", u"高", u"講談。ぴあの区分どおりowarai。"),
"5189": ("owarai", u"高", u""),
"5191": ("engeki", u"低", u"ぴあ=演劇/朗読・リーディング→対応表ではengeki。ただしぴあのタグは「アニメ・声優・ゲーム」で、フラガリアメモリーズは声優が主役のメディアミックス企画。seiyuuに置いたほうがファンは見つけやすいかもしれない。"),
"5193": ("engeki", u"高", u""),
"5194": ("art", u"中", u"ぴあ=イベント/博覧会・展示会・見本市→対応表どおりart。実体は国際園芸博覧会（横浜・旧上瀬谷通信施設）でアート色は薄く、対応表に従っただけ。"),
"5195": ("engeki", u"高", u""),
"5197": ("art", u"低", u"ぴあ=イベント/イベントその他（対応表に無い区分）。実体は「バイオハザード」30周年の大型展覧会（BEAMギャラリー）なので展示会扱いでartにした。ただしぴあのタグは「アニメ・声優・ゲーム」で、animeに置く選択肢もある。"),
"5198": ("sports", u"高", u""),
"5199": ("sports", u"高", u""),
"5200": ("sports", u"高", u""),
}

out = {}
missing = []
for it in items:
    i = str(it["id"])
    v = ext[i]
    sub = v["sub"]
    if sub:
        sub = sub.replace(u" ", u"/", 1)
    else:
        cds = v["genreCd"] or v["genreCdAny"]
        sub = CDSUB.get(cds[0]) if cds else None
    if i not in D:
        missing.append(i); continue
    g, c, n = D[i]
    out[i] = {"pia_sub": sub, "genre": g, "confidence": c, "note": n}

assert not missing, missing
assert len(out) == len(items), (len(out), len(items))
json.dump(out, open(os.path.join(BASE, "tmp/genre_out_0825.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
import collections
print("wrote", len(out))
print(collections.Counter(v["genre"] for v in out.values()).most_common())
print(collections.Counter(v["confidence"] for v in out.values()).most_common())
print("nullsub", [k for k,v in out.items() if not v["pia_sub"]])
