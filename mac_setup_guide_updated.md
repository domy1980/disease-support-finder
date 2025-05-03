# Mac セットアップガイド（更新版）

このガイドでは、難病・希少疾患支援団体検索アプリケーションをMacで実行するための環境セットアップ手順を説明します。特に、ローカルLLMを使用した拡張機能の設定に焦点を当てています。

## 目次

1. [必要条件](#必要条件)
2. [バックエンドのセットアップ](#バックエンドのセットアップ)
3. [フロントエンドのセットアップ](#フロントエンドのセットアップ)
4. [Ollamaのセットアップ](#ollamaのセットアップ)
5. [MLXのセットアップ](#mlxのセットアップ)
6. [4ビット量子化モデルの使用](#4ビット量子化モデルの使用)
7. [アプリケーションの起動](#アプリケーションの起動)
8. [トラブルシューティング](#トラブルシューティング)

## 必要条件

- macOS 12以降（M1/M2/M3/M4チップ推奨）
- 最低16GB RAM（32GB以上推奨）
- 最低50GBの空き容量
- Homebrew
- Python 3.10以上
- Node.js 18以上
- Git

## バックエンドのセットアップ

1. リポジトリをクローン:

```bash
git clone https://github.com/domy1980/disease-support-finder.git
cd disease-support-finder
```

2. Poetryをインストール（まだの場合）:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. バックエンドの依存関係をインストール:

```bash
cd backend/disease-support-backend
poetry install
```

## フロントエンドのセットアップ

1. Node.jsとnpmがインストールされていることを確認:

```bash
node -v  # v18.x.x以上
npm -v   # v8.x.x以上
```

2. フロントエンドの依存関係をインストール:

```bash
cd ../../frontend
npm install
```

## Ollamaのセットアップ

1. Ollamaをインストール:

```bash
brew install ollama
```

2. Ollamaを起動:

```bash
ollama serve
```

3. 推奨モデルをダウンロード（別のターミナルで実行）:

```bash
# Llama4 7B（基本モデル）
ollama pull llama4:7b

# Llama4 Scout（検索と情報抽出に最適化）
ollama pull llama4-scout:8b-q4_0

# Llama4 Maverick（高度な推論能力）
ollama pull llama4-maverick:8b-q4_0

# Mistral（バランスの取れた性能）
ollama pull mistral:latest
```

### 4ビット量子化モデルの使用

Llama4 ScoutとLlama4 Maverickは4ビット量子化バージョン（q4_0）を使用することで、メモリ使用量を大幅に削減しながら高い性能を維持できます：

```bash
# 4ビット量子化版Llama4 Scout
ollama pull llama4-scout:8b-q4_0

# 4ビット量子化版Llama4 Maverick
ollama pull llama4-maverick:8b-q4_0
```

これらの量子化モデルは、通常のモデルと比較して：
- メモリ使用量: 約75%削減（8GBのモデルが約2GB程度に）
- 推論速度: 約2倍高速
- 精度: わずかな低下（ほとんどのタスクで許容範囲内）

M4 Maxなどの高性能MacBookでは、これらの量子化モデルを使用することで、複数のモデルを同時に実行したり、他のアプリケーションと並行して使用したりすることが可能になります。

## MLXのセットアップ

MLXはApple Silicon（M1/M2/M3/M4チップ）向けに最適化された機械学習フレームワークで、Qwenモデルを高速に実行できます。

1. MLXをインストール:

```bash
pip install mlx mlx-lm
```

2. Qwenモデルをダウンロード（4ビット量子化版）:

```bash
# ディレクトリを作成
mkdir -p ~/mlx-models

# Qwen 4B（バランスの取れたモデル）
git clone https://huggingface.co/mlx-community/Qwen1.5-4B-Chat-4bit ~/mlx-models/Qwen/Qwen1.5-4B-Chat-4bit

# Qwen 7B（高性能モデル）
git clone https://huggingface.co/mlx-community/Qwen1.5-7B-Chat-4bit ~/mlx-models/Qwen/Qwen1.5-7B-Chat-4bit

# Qwen 1.8B（軽量モデル）
git clone https://huggingface.co/mlx-community/Qwen1.5-1.8B-Chat-4bit ~/mlx-models/Qwen/Qwen1.5-1.8B-Chat-4bit

# Qwen 30B A3B（医療特化モデル - M4 Max 128GB推奨）
git clone https://huggingface.co/mlx-community/Qwen-30B-A3B-4bit ~/mlx-models/mlx-community/Qwen-30B-A3B-4bit

# Qwen2 7B（最新世代モデル）
git clone https://huggingface.co/mlx-community/Qwen2-7B-Instruct-4bit ~/mlx-models/Qwen/Qwen2-7B-Instruct-4bit

# Qwen2 72B（最新世代大規模モデル - M4 Max 128GB推奨）
git clone https://huggingface.co/mlx-community/Qwen2-72B-Instruct-4bit ~/mlx-models/Qwen/Qwen2-72B-Instruct-4bit

# Llama 3 8B（高性能モデル）
git clone https://huggingface.co/mlx-community/Llama-3-8B-Instruct-4bit ~/mlx-models/mlx-community/Llama-3-8B-Instruct-4bit
```

3. MLX APIサーバーを起動（オプション）:

```bash
# MLX APIサーバーをインストール
pip install mlx-server

# サーバーを起動（Qwen 4Bモデル）
mlx-server --model ~/mlx-models/Qwen/Qwen1.5-4B-Chat-4bit --port 8080
```

4. または、直接Pythonから実行することも可能:

```bash
# モデルを直接実行（APIサーバーなし）
python -m mlx_lm.generate --model ~/mlx-models/Qwen/Qwen1.5-4B-Chat-4bit --prompt "こんにちは、元気ですか？"
```

MLXの利点:
- Apple Silicon向けに最適化された高速な推論
- 低メモリ使用量（4ビット量子化モデル）
- バッテリー効率の良い実行
- APIサーバーまたは直接実行の両方をサポート

## アプリケーションの起動

1. バックエンドを起動（LLM拡張機能付き）:

```bash
cd backend/disease-support-backend
poetry run uvicorn app.main_llm_enhanced:app --reload --host 0.0.0.0 --port 8001
```

2. フロントエンドを起動（別のターミナルで）:

```bash
cd frontend
npm run dev
```

3. ブラウザで http://localhost:5173 にアクセス

## トラブルシューティング

### メモリ不足エラー

LLMモデルを実行中にメモリ不足エラーが発生した場合:

1. 4ビット量子化モデル（q4_0）を使用する
2. 他の大きなアプリケーションを閉じる
3. スワップメモリを増やす:

```bash
sudo sysctl -w vm.swappiness=100
```

### Ollamaサーバーの問題

Ollamaサーバーに接続できない場合:

1. Ollamaが実行中か確認:

```bash
ps aux | grep ollama
```

2. 必要に応じて再起動:

```bash
killall ollama
ollama serve
```

### LM Studioの問題

LM Studioサーバーに接続できない場合:

1. LM Studioアプリが実行中か確認
2. 「Local Inference Server」タブでサーバーが起動しているか確認
3. ポート1234が他のアプリケーションで使用されていないか確認:

```bash
lsof -i :1234
```

### M4 Max最適化設定

M4 Max MacBook Proでの最適化設定:

1. 複数のLLMを同時に実行する場合は、4ビット量子化モデルを使用
2. メモリプレッシャーを監視（Activityモニタ）
3. 必要に応じてスワップメモリを増やす:

```bash
sudo sysctl -w vm.swappiness=100
```

4. 高性能モードを有効にする（バッテリー設定から）
