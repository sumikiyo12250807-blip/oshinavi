# 9/11発売ぶんのX予約の段取り（2026-09-10 夜）

## 予約時刻＝**10分おき・20:01スタート**

台本と memory feedback_x_schedule_interval ＝
「20:01スタート／分は半端（きりのいい分＋1分）／**本数が増えたら間隔は詰める**」。
15分おきだと7本で21:31まで伸びるので、**10分おき**にして21:01で終わらせる。
（実績＝5〜6本は15分おき、9本は5分おき）

| # | 時刻 | 中身 | URL |
|---|---|---|---|
| 1 | **20:01** | 主役 なとり | `oshinavi.jp/?q=なとり` |
| 2 | **20:11** | 主役 野村萬斎 | `oshinavi.jp/?q=野村萬斎` |
| 3 | **20:21** | 主役 春風亭昇太 | `oshinavi.jp/?q=春風亭昇太` |
| 4 | **20:31** | まとめ クラシックとジャズ | `oshinavi.jp/?genre=classic&status=urgent` |
| 5 | **20:41** | まとめ 落語・お笑い | `oshinavi.jp/?genre=owarai&status=urgent` |
| 6 | **20:51** | まとめ 音楽（JPOPほか） | `oshinavi.jp/?genre=jpop&status=urgent` |
| 7 | **21:01** | まとめ 舞台・伝統芸能・スポーツ・展示 | `oshinavi.jp/?genre=engeki&status=urgent` |

## 「このあとの投稿では」の予告がつながっているか（確認済み）

- 1本目 → 「狂言など伝統芸能」＝2本目（野村萬斎）✅
- 2本目 → 「落語」＝3本目（春風亭昇太）✅
- 3本目 → 「クラシックとジャズ」＝4本目 ✅
- 4本目 → 「落語とお笑い」＝5本目 ✅
- 5本目 → 「JPOPなどの音楽」＝6本目 ✅
- 6本目 → 「舞台・伝統芸能・スポーツ・展示」＝7本目 ✅
- 7本目 → 「明日の夜は9/12発売のチケット」＋「これで全部」（最後の1本だけ）✅

## 予約の手順（memory feedback_x_paste_powershell_only）

**1本あたり約4分＝7本で約28分。20:01に間に合わせるなら19:30には操作を始める。**

1. `Get-Content -Raw -Encoding UTF8 tmp/xp0911/NN.txt | Set-Clipboard`
2. 拡張で `x.com/compose/post` → `find` で `textbox "Post text"`（ダイアログ内）をクリック
3. **`tmp/x_paste_0910.ps1`** を実行（Chromeを前面に出して `SendKeys("^v")`）
4. `javascript_tool` で入った字数を機械で確かめる
5. `Schedule post` を URLが `/compose/post/schedule` に変わるまで押す（1〜3回）
6. `form_input` で Hour / Minute → 「Will send on ...」を読む → `Confirm`
7. `Schedule` を2回（1回目はホバー）→ トーストで時刻を確認
8. 最後に `x.com/compose/post/unsent/scheduled` で**全時刻を機械照合**

🚨`.ps1` に日本語を1文字も書かない（PowerShell 5.1 がANSIで読んで壊れる）。
🚨**ブラウザのタブが背面だとXは描画されない**。予約の前にタブを前面に出す＝
   ユーザーがOSHINAVIの画面を見ているので、**切り替える前に一声かける**。
