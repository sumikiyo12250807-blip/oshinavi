const PREFECTURE_TO_REGION = {
    "北海道": "hokkaido",
    "青森": "tohoku", "岩手": "tohoku", "宮城": "tohoku",
    "秋田": "tohoku", "山形": "tohoku", "福島": "tohoku",
    "茨城": "kanto",  "栃木": "kanto",  "群馬": "kanto",
    "埼玉": "kanto",  "千葉": "kanto",  "東京": "kanto",  "神奈川": "kanto",
    "新潟": "chubu",  "富山": "chubu",  "石川": "chubu",  "福井": "chubu",
    "山梨": "chubu",  "長野": "chubu",  "岐阜": "chubu",  "静岡": "chubu",  "愛知": "chubu",
    "三重": "kinki",  "滋賀": "kinki",  "京都": "kinki",  "大阪": "kinki",
    "兵庫": "kinki",  "奈良": "kinki",  "和歌山": "kinki",
    "鳥取": "chugoku","島根": "chugoku","岡山": "chugoku","広島": "chugoku","山口": "chugoku",
    "徳島": "shikoku","香川": "shikoku","愛媛": "shikoku","高知": "shikoku",
    "福岡": "kyushu", "佐賀": "kyushu", "長崎": "kyushu", "熊本": "kyushu",
    "大分": "kyushu", "宮崎": "kyushu", "鹿児島": "kyushu","沖縄": "kyushu",
    // 海外公演（ぴあが日本の県を持たない興行）。バッジの「（台湾 M/D公演）」から拾う
    "台湾": "kaigai",
  };
const PREF_LIST = Object.keys(PREFECTURE_TO_REGION);
  function parseDateStr(str) {
    const [y, m, d] = str.split("-").map(Number);
    return new Date(y, m - 1, d);
  }
const today = new Date(2026, 7, 14);
  function isTicketActive(t) {
    if (t.saleUntilSoldOut) return true;
    if ((!t.startDate || parseDateStr(t.startDate) <= today) && parseDateStr(t.date) < today) return false;
    return true;
  }
  function eventRegions(ev) {
    const set = new Set();
    // まず「まだ買える」枠の種別から県名を拾う（複数公演で一部だけ期限切れ／別県の場合に正確）。
    // prefecture が複合（「宮城/広島/新潟」等）でも、期限切れ公演の県はここで除外される。
    let text = (ev.tickets || []).filter(isTicketActive).map(t => t.type || "").join(" ");
    if (!PREF_LIST.some(p => text.includes(p))) {
      // アクティブ枠に県名が無い場合のフォールバック
      if (ev.prefecture && ev.prefecture !== "全国") {
        text = ev.prefecture;                                  // 単独公演など
      } else {
        text = (ev.venue || "") + " " + (ev.dateLabel || "");  // 全国かつ枠に県名なし
      }
    }
    const scan = text.replace(/東京/g, "東京_"); // 「京都」が「東京都」に誤マッチしないよう分離
    PREF_LIST.forEach(p => {
      const hay = (p === "京都") ? scan : text;
      if (hay.includes(p)) set.add(PREFECTURE_TO_REGION[p]);
    });
    return set;
  }
const ev = {"id": 4259, "artist": "≪当選者限定≫佐藤大樹 2nd写真集『In Motion』発売記念 in 台北", "name": "≪当選者限定≫佐藤大樹 2nd写真集『In Motion』発売記念 in 台北", "date": "2026-10-17", "dateLabel": "2026年10月17日(土) 台湾 台北市某所", "venue": "台北市某所", "prefecture": "台湾", "genre": "fanevent", "price": null, "links": {"rakuten": null, "lawson": null, "pia": "https://t.pia.jp/pia/event/event.do?eventCd=2631533", "eplus": null}, "tickets": [{"type": "一般発売（台湾 10/17公演）8/21 16:00発売", "date": "2026-08-21", "startDate": "2026-08-21"}], "verified": true, "verifiedAt": "2026-08-14"};
console.log("id4259 の所属エリア =", JSON.stringify([...eventRegions(ev)]));