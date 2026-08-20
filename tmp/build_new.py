# -*- coding: utf-8 -*-
import re, json, unicodedata, urllib.parse

def h(s):
    return unicodedata.normalize('NFKC', s)

def amz(term):
    return "https://www.amazon.co.jp/s?k=%s&i=specialty-aps&srs=26200021051&tag=oshinavi0a-22" % urllib.parse.quote(term)

def pia(cd):
    return "https://t.pia.jp/pia/event/event.do?" + cd

# (artist, name, dateISO, dateLabel, venue, pref, pia_cd, ticket_type, sale_dateISO, amazon_term_or_None)
E = [
("佐藤ひらり","佐藤ひらり","2026-09-18","2026年9月18日(金)","なかのZERO 小ホール","東京","eventCd=2619104","一般発売 6/11 10:00発売","2026-06-11","佐藤ひらり"),
("SHAG","SHAG (SUGIZO/KenKen ほか)","2026-09-28","2026年9月28日(月)","BLUES ALLEY JAPAN","東京","eventCd=2621067","一般発売 6/11 14:00発売","2026-06-11","SHAG SUGIZO"),
("ジェイコブ・コーラー","ジェイコブ・コーラー (ゲスト:みやけん/後藤浩二)","2026-08-28","2026年8月28日(金)","Niterra日本特殊陶業市民会館 フォレストホール","愛知","eventCd=2616793","一般発売 6/11 10:00発売","2026-06-11","ジェイコブコーラー"),
("倍賞千恵子","マザーセキュリティpresents 倍賞千恵子コンサート2026 with小六禮次郎","2026-10-11","2026年10月11日(日)","中日ホール","愛知","eventCd=2621277","一般発売 6/11 10:00発売","2026-06-11","倍賞千恵子"),
("todle/plop","SPIRITUAL LOUNGE & plop presents \"CHAT\"","2026-07-10","2026年7月10日(金)","SPIRITUAL LOUNGE","北海道","eventCd=2622922","一般発売 6/12 10:00発売","2026-06-12",None),
("yosugala","なぎちゃん爆誕カーニバル4th","2026-07-05","2026年7月5日(日)","LIQUIDROOM","東京","eventCd=2621120","一般発売 6/12 12:00発売","2026-06-12",None),
("HANDSIGN","HANDSIGNコンサート","2026-08-16","2026年8月16日(日)","一宮市尾西市民会館","愛知","eventCd=2619896","一般発売 6/12 11:00発売","2026-06-12","HANDSIGN"),
("Baby Boo","Baby Boo","2026-09-27","2026年9月27日(日)","町田市民ホール","東京","eventCd=2616983","一般発売 6/12 10:00発売","2026-06-12","Baby Boo"),
("RHYMESTER/Zeebra ほか","横芝光町 STREET TO B","2026-10-11","2026年10月11日(日)","ふれあい坂田池公園陸上競技場","千葉","eventCd=2620203","早割チケット 6/12 10:00発売","2026-06-12",None),
("アニソン3ライブ","アニソン3(スリー)ライブ 2026 in 河内長野","2026-09-26","2026年9月26日(土)","ラブリーホール 大ホール","大阪","eventCd=2615206","一般発売 6/13 10:00発売","2026-06-13",None),
("go!go!vanillas/KANA-BOON ほか","30th Anniversary Special Talking Rock! FES.2026 神戸編","2026-08-09","2026年8月8日(土)・9日(日)","ワールド記念ホール","兵庫","eventCd=2622261","一般発売 6/13 10:00発売","2026-06-13",None),
("沖仁","沖仁カルテット with U-zhaan","2026-10-03","2026年10月3日(土)","行徳文化ホール I&I","千葉","eventCd=2620062","一般発売 6/13 10:00発売","2026-06-13","沖仁"),
("cinema staff/9mm Parabellum Bullet","cinema staff/9mm Parabellum Bullet (ROCK the ROCK!!)","2026-06-20","2026年6月20日(土)","池下CLUB UPSET","愛知","eventCd=2621519","一般発売 6/13 12:00発売","2026-06-13","9mm Parabellum Bullet"),
("SINON","SINON 奇跡の歌声～カーペンターズコンサートin黒崎～","2026-10-10","2026年10月10日(土)","黒崎ひびしんホール 大ホール","福岡","eventCd=2616784","一般発売 6/13 10:00発売","2026-06-13",None),
("the shes gone/メレンゲ","SHINJUKU LOFT 50th ANNIVERSARY DREAM MATCH 2026","2026-08-27","2026年8月27日(木)","新宿LOFT","東京","eventCd=2618973","一般発売 6/13 10:00発売","2026-06-13",None),
("JOIN ALIVE","JOIN ALIVE 2026","2026-07-19","2026年7月18日(土)・19日(日)","いわみざわ公園","北海道","eventBundleCd=b2668580","一般発売 6/13 10:00発売","2026-06-13",None),
("鈴木実貴子ズ","鈴木実貴子ズ","2026-07-30","2026年7月30日(木)","LIVE HOUSE FEVER","東京","eventBundleCd=b2668122","一般発売 6/13 10:00発売","2026-06-13","鈴木実貴子ズ"),
("須藤寿","須藤寿 GATALI ACOUSTIC SET","2026-08-07","2026年8月7日(金)","Live Hall クラブ月世界","兵庫","eventCd=2614550","一般発売 6/13 10:00発売","2026-06-13","須藤寿"),
("須藤寿","須藤寿 GATALI ACOUSTIC SETの大団円","2026-08-19","2026年8月19日(水)","duo MUSIC EXCHANGE","東京","eventBundleCd=b2666997","一般発売 6/13 10:00発売","2026-06-13","須藤寿"),
("SU","SU (スー)","2026-07-03","2026年7月3日(金)","FREEDOM","大分","eventCd=2622637","一般発売 6/13 10:00発売","2026-06-13",None),
("竹原ピストル","竹原ピストル 四国ツアー","2026-09-05","2026年9月5日(土)ほか","DIME(香川)/W studio RED(愛媛)/高知/徳島","香川","eventCd=2618185","一般発売 6/13 10:00発売","2026-06-13","竹原ピストル"),
("DIMENSION","DIMENSION","2026-07-19","2026年7月19日(日)","大手町三井ホール","東京","eventCd=2609310","一般発売 6/13 10:00発売","2026-06-13","DIMENSION"),
("toe","toe","2026-10-04","2026年10月4日(日)","Zepp Namba(OSAKA)","大阪","eventCd=2620618","一般発売 6/13 10:00発売","2026-06-13","toe"),
("中村雅俊","中村雅俊","2026-09-13","2026年9月13日(日)","氷見市芸術文化館 ホール","富山","eventCd=2547059","一般発売 6/13 10:00発売","2026-06-13","中村雅俊"),
("ハロプロ研修生","Hello!Project 研修生発表会 2026 6月 ～若葉～","2026-06-28","2026年6月28日(日)","Zepp DiverCity(TOKYO)","東京","eventCd=2619789","一般発売 6/13 10:00発売","2026-06-13",None),
("杉真理/伊豆田洋之/山本英美","ピュアミュージック 2026『残暑お見舞いツアー』","2026-09-11","2026年9月11日(金)","CLUB CITTA'","神奈川","eventCd=2615100","一般発売 6/13 10:00発売","2026-06-13",None),
("FouRTe","FouRTe Project","2026-08-14","2026年8月14日(金)","Zepp DiverCity(TOKYO)","東京","eventCd=2621530","プリセール先行 6/13 12:00発売","2026-06-13",None),
("04 Limited Sazabys","04 Limited Sazabys","2026-10-02","2026年10月2日(金)ほか","Zepp Haneda(TOKYO)/KT Zepp Yokohama","東京","eventCd=2611071","一般発売 6/13 12:00発売","2026-06-13","04 Limited Sazabys"),
("二見颯一","二見颯一","2026-09-04","2026年9月4日(金)・5日(土)","神戸朝日ホール(兵庫)/やまと郡山城ホール(奈良)","兵庫","eventCd=2620209","一般発売 6/13 10:00発売","2026-06-13","二見颯一"),
("BREAKERZ","BREAKERZ","2026-07-25","2026年7月25日(土)","恵比寿ザ・ガーデンホール","東京","eventBundleCd=b2666022","一般発売 6/13 10:00発売","2026-06-13","BREAKERZ"),
("牧野由依","牧野由依","2026-08-11","2026年8月11日(火・祝)","浜離宮朝日ホール","東京","eventCd=2540765","一般発売 6/13 10:00発売","2026-06-13","牧野由依"),
("南こうせつ","南こうせつ","2026-09-10","2026年9月10日(木)","トークネットホール仙台 大ホール","宮城","eventCd=2605553","一般発売 6/13 10:00発売","2026-06-13","南こうせつ"),
("メランコリックサーカス","MELANCHOLIC CIRCUS","2026-09-26","2026年9月26日(土)","池下CLUB UPSET","愛知","eventCd=2622462","一般発売 6/13 10:00発売","2026-06-13",None),
("ゆいゆいシスターズ","ゆいゆいシスターズ (ゲスト:大城貴幸)","2026-10-30","2026年10月30日(金)","世界館","大阪","eventCd=2622772","一般発売 6/13 10:00発売","2026-06-13",None),
("由薫","由薫","2026-08-21","2026年8月21日(金)","BLUE Enoshima","神奈川","eventCd=2620595","一般発売 6/13 10:00発売","2026-06-13","由薫"),
("友希","友希","2026-08-23","2026年8月23日(日)ほか","LIVE HOUSE Hearts(埼玉)/SPACE ODD/Zepp Shinjuku","埼玉","eventCd=2619471","一般発売 6/13 10:00発売","2026-06-13","友希"),
("ユン・サンヒョン","YOON SANG HYUN JAPAN MINI LIVE \"Blue Memories\"","2026-06-27","2026年6月27日(土)","ENSQUARE LIVE HALL","東京","eventCd=2621818","一般発売 6/13 12:00発売","2026-06-13",None),
("吉幾三","吉幾三コンサート 2026","2026-09-13","2026年9月13日(日)","静岡市清水文化会館マリナート 大ホール","静岡","eventCd=2611801","一般発売 6/13 10:00発売","2026-06-13","吉幾三"),
("betcover!!/OGRE YOU ASSHOLE","ライブナタリー \"betcover!! × OGRE YOU ASSHOLE\"","2026-07-30","2026年7月30日(木)","BIGCAT","大阪","eventBundleCd=b2667963","一般発売 6/13 12:00発売","2026-06-13",None),
("Liella!","ラブライブ!スーパースター!! Liella!のちゅーとりえらいぶ!! 2026","2026-08-02","2026年8月1日(土)・2日(日)","LaLa arena TOKYO-BAY","千葉","eventBundleCd=b2665770","一般発売 6/13 12:00発売","2026-06-13","Liella"),
("小椋佳","小椋佳","2026-09-12","2026年9月12日(土)","富岡市かぶら文化ホール","群馬","eventCd=2617459","一般発売 6/14 10:00発売","2026-06-14","小椋佳"),
("志多ら","志多ら 新城公演「音還～おんがえし～」","2026-09-13","2026年9月13日(日)","新城文化会館 大ホール","愛知","eventCd=2616809","一般発売 6/14 10:00発売","2026-06-14","志多ら"),
("和太鼓グループ彩-sai-","衝動X あの日、生まれた「衝動」を確信へ","2026-10-10","2026年10月10日(土)","THEATRE1010","東京","eventBundleCd=b2667347","一般発売 6/14 10:00発売","2026-06-14",None),
("高嶋弘之","高嶋弘之 私の好きな昭和歌謡in松浦","2026-09-27","2026年9月27日(日)","松浦市文化会館 ゆめホール","長崎","eventCd=2616401","一般発売 6/14 10:00発売","2026-06-14",None),
("伊藤政則","HEAVY METAL SOUNDHOUSE 45th ANNIVERSARY SPECIAL ～SUMMER SCHOOL 2026～","2026-08-09","2026年8月9日(日)","SPACE ODD","東京","eventCd=2622349","一般発売 6/14 10:00発売","2026-06-14",None),
("lynch.","lynch.","2026-09-26","2026年9月26日(土)・27日(日)","DRUM LOGOS(福岡)/熊本B.9 V1","福岡","eventCd=2616561","一般発売 6/14 10:00発売","2026-06-14","lynch."),
("ROCKGEN","ROCKGEN -六弦-","2026-10-04","2026年10月4日(日)","宗次ホール","愛知","eventCd=2620334","一般発売 6/14 10:00発売","2026-06-14",None),
("ちひろ","ちひろCONCERT 金子みすゞの心とともに","2026-10-08","2026年10月8日(木)","郡山市立中央公民館 多目的ホール","福島","eventCd=2617196","一般発売 6/15 10:00発売","2026-06-15",None),
("林部智史","林部智史 Dining&Concert 2026","2026-08-02","2026年8月2日(日)","神戸ポートピアホテル 大輪田の間","兵庫","eventCd=2619569","一般発売 6/15 10:00発売","2026-06-15","林部智史"),
("島袋優(BEGIN)/川満ゆうき","優とゆうき そしてリョーサ ～Guitar Bro!～","2026-08-23","2026年8月23日(日)","LIVE HOUSE MOD'S","沖縄","eventCd=2620746","一般発売 6/15 10:00発売","2026-06-15",None),
]

assert len(E) == 50, len(E)

# parse EVENTS array end
c = open('index.html', encoding='utf-8').read()
mstart = re.search(r'const\s+EVENTS\s*=\s*\[', c)
arr_open = c.index('[', mstart.start())
i = arr_open; depth = 0; in_str = False; esc = False; BS = chr(92); arr_close = None
while i < len(c):
    ch = c[i]
    if in_str:
        if esc: esc = False
        elif ch == BS: esc = True
        elif ch == '"': in_str = False
    else:
        if ch == '"': in_str = True
        elif ch == '[' or ch == '{': depth += 1
        elif ch == ']' or ch == '}':
            depth -= 1
            if depth == 0 and ch == ']':
                arr_close = i; break
    i += 1
assert arr_close is not None

# find last '}' before arr_close (end of last element)
last = c.rfind('}', 0, arr_close)

nid = 551; order = []; objs = []
for (artist,name,date,dlabel,venue,pref,cd,ttype,sdate,amzterm) in E:
    links = {"rakuten": None, "lawson": None, "pia": pia(cd), "eplus": None}
    if amzterm: links["amazon"] = amz(amzterm)
    obj = {"id": nid, "artist": h(artist), "name": h(name), "date": date, "dateLabel": dlabel,
           "venue": h(venue), "prefecture": pref, "genre": "new", "price": None, "links": links,
           "tickets": [{"type": h(ttype), "startDate": sdate, "date": sdate}],
           "verified": True, "verifiedAt": "2026-06-10"}
    objs.append(obj); order.append(nid); nid += 1

# serialize each object with 12-space base indent to match file style
def ser(o):
    s = json.dumps(o, ensure_ascii=False, indent=6)
    # indent every line by 6 spaces so it nests under the array (existing uses 6-space element indent)
    lines = s.split("\n")
    out = []
    for j, ln in enumerate(lines):
        out.append("      " + ln)
    return "\n".join(out)

block = ",\n" + ",\n".join(ser(o) for o in objs)
new_c = c[:last+1] + block + c[last+1:]

# update NEW_ORDER
new_c = new_c.replace("const NEW_ORDER = [];", "const NEW_ORDER = [" + ",".join(str(x) for x in order) + "];", 1)

open('index.html', 'w', encoding='utf-8').write(new_c)
print("inserted", len(objs), "entries; ids", order[0], "-", order[-1])
