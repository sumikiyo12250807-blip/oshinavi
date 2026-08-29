# MiniMax Music 3 を ComfyUI から使う（2026-08-29 セットアップ）

## いまの状態

| | 使えるか | 理由 |
|---|---|---|
| **fal.ai 経由**（既定） | ⏳ **APIキーを入れれば使える** | MiniMax Music 3 を1生成 **$0.035** で提供。新規登録OK |
| **MiniMax公式API** | ❌ 使えない | **2026-08-20に新規ユーザーへ閉鎖**。実測で `music-3.0` / `music-2.6` / `*-free` すべて HTTP 410（status_code 2153）。「既に音楽APIを課金利用していたアカウント」だけ継続可 |
| **ローカル実行**（ComfyUI標準ノード） | ❌ このPCでは無理 | CUDA必須。重みは最小のINT8構成でも約12GB（DiT 2.5GB＋テキストエンコーダ 9.2GB＋VAE 0.22GB）。このPCは Intel HD Graphics 620・メモリ16GB |

## 使いはじめ

1. **fal.ai のAPIキーを取る** … https://fal.ai/dashboard/keys
2. キーを次のどれかに置く
   - このフォルダに `fal_key.txt` として保存（中身はキーだけ・改行不要）
   - または環境変数 `FAL_KEY`
3. `C:\Users\user\ComfyUI\ComfyUI起動.bat` をダブルクリック
4. ブラウザで http://127.0.0.1:8188
5. ノードを追加 … 右クリック → `MiniMax Music` → **MiniMax Music 3 (Cloud)**
6. `audio` 出力を **SaveAudio** か **PreviewAudio** につなぐ

## ノードの設定

| 項目 | 意味 |
|---|---|
| `provider` | `fal`（既定）／`minimax`（公式・既存課金者のみ） |
| `prompt` | 曲の説明。ジャンル・雰囲気・楽器・ボーカルの性別など（**1〜2000字**） |
| `lyrics` | 歌詞。`[verse]` `[chorus]` などの構造タグは**それぞれ独立した行**に置くこと（**1〜3500字**） |
| `is_instrumental` | ON で歌なし。fal では歌詞欄が自動で `[instrumental]` になる |
| `duration` | fal のみ。曲の長さ（秒・既定60） |
| `num_inference_steps` / `guidance_scale` / `seed` | fal のみの生成パラメータ |
| `minimax_model` ほか | `provider=minimax` の時だけ効く |

`info` 出力に、かかった時間・秒数・request_id が出るので、うまくいかない時はそこを見てね。

## 注意

- 生成はクラウド側で走るので**このPCのGPUは使わない**。CPUモードのComfyUIで問題なし。
- fal は**キュー方式**（投げて→ポーリング）。長い曲ほど待つので `timeout_sec` を伸ばす。
- 課金は fal.ai 側で発生する（1生成 $0.035）。

## もしGPUのあるPCに移すなら

ComfyUI標準の `MiniMax Music3 Text Encode` / `Empty MiniMax Music3 Latent Audio` ノードでローカル生成できる。
モデルは https://huggingface.co/Comfy-Org/MiniMax-Music-3 から
`diffusion_models/` `text_encoders/` `vae/` の3つを ComfyUI の同名フォルダへ。
