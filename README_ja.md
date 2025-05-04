# 難病・希少疾患支援団体検索アプリケーション

このアプリケーションは、日本の指定難病や小児慢性特定疾病の患者さんとそのご家族を支援するための団体情報を簡単に検索・管理できるツールです。

## 機能概要

- **疾患検索**: 2,871件の指定難病・小児慢性特定疾病から検索
- **支援団体情報**: 患者会、家族会、支援団体、医療機関などの情報を自動収集
- **データ管理**: 手動でのデータ追加や編集が可能
- **ウェブサイト監視**: 団体サイトの稼働状況を追跡
- **高度な分析**: ローカルLLMを活用した医療情報の詳細分析

## システム要件

- **バックエンド**: Python 3.8以上、FastAPI
- **フロントエンド**: Node.js 16以上、React、TypeScript
- **ローカルLLM**: MacBook M4 Max 128GB推奨（Metal GPU加速対応）

## セットアップ方法

### バックエンドのセットアップ

```bash
# リポジトリのクローン
git clone https://github.com/domy1980/disease-support-finder.git
cd disease-support-finder

# バックエンドの依存関係インストール
cd backend/disease-support-backend
poetry install

# 開発サーバーの起動
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### フロントエンドのセットアップ

```bash
# フロントエンドディレクトリに移動
cd ../../frontend

# 依存関係のインストール
npm install

# 開発サーバーの起動
npm run dev
```

## ローカルLLMのセットアップ

本アプリケーションは以下のローカルLLMプロバイダーをサポートしています：

1. **Ollama**: Mistral、Llama 3などの標準モデル
2. **MLX**: Apple Silicon向け最適化モデル
3. **LM Studio**: 多様なモデルをGUIで管理
4. **llama.cpp**: Metal GPU加速による高性能モデル実行

各プロバイダーの詳細なセットアップ方法は以下のガイドを参照してください：

- [Ollamaセットアップガイド](mac_setup_guide_updated.md)
- [MLXセットアップガイド](mlx_setup_guide.md)
- [LM Studioセットアップガイド](lmstudio_setup_guide.md)
- [llama.cppセットアップガイド](llamacpp_setup_guide.md)
- [Unsloth Llama4セットアップガイド](unsloth_setup_guide.md)

## 使用方法

1. ブラウザで `http://localhost:5173` にアクセス
2. 疾患名を入力して検索（例：「白血病」「筋ジストロフィー」）
3. 検索結果から疾患を選択して詳細表示
4. 支援団体情報の確認や手動データの追加が可能

## LLM機能の使用方法

1. LLMプロバイダー設定パネルでプロバイダーとモデルを選択
2. 疾患を選択して「LLM検索実行」ボタンをクリック
3. バックグラウンドで支援団体情報の検索と分析が実行される
4. 結果は自動的に保存され、UIに表示される

## 推奨モデル

### 標準モデル（Ollama）
- **Mistral**: バランスの取れた性能と速度（デフォルト）
- **Llama 3 (70B)**: 最高の精度（M4 Max 128GBで実行可能）

### Metal最適化モデル
- **Qwen30B-A3B**: 医療ドメイン特化の高性能モデル
- **Qwen32B**: 大規模言語理解に優れたモデル
- **Phi-4 reasoning-plus-8bit**: 推論能力に優れたMicrosoftモデル

### Unsloth Llama4モデル
- **Llama-4-Scout-17B-16E-Instruct-GGUF:Q2_K_XL**: 超高速（Q2量子化）
- **Llama-4-Scout-17B-16E-Instruct-GGUF:Q4_K_XL**: 高精度（Q4量子化）

## 貢献方法

1. リポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチをプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## ライセンス

MITライセンスの下で配布されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 謝辞

このプロジェクトは、日本の難病・希少疾患患者さんとそのご家族を支援するために開発されました。データ提供にご協力いただいた関係者の皆様に感謝いたします。
