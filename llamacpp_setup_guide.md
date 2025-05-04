# llama.cpp セットアップガイド for MacBook M4 Max

このガイドでは、MacBook M4 Max上でllama.cppを使用して高性能なLLMモデルを実行する方法を説明します。llama.cppは、C++で実装された高速なLLMフレームワークで、Metal GPUアクセラレーションをサポートしています。

## 前提条件

- MacBook M4 Max（128GB RAM推奨）
- Homebrewがインストール済み
- ターミナルの基本的な知識

## llama.cppのインストール

### 1. Homebrewを使用したインストール

```bash
# llama.cppをインストール
brew install llama.cpp
```

### 2. ソースからのビルド（オプション - より高度なカスタマイズが必要な場合）

```bash
# 必要なツールのインストール
brew install cmake

# リポジトリのクローン
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp

# Metal GPUサポート付きでビルド
LLAMA_METAL=1 make
```

## モデルのセットアップ

### 1. モデルディレクトリの作成

```bash
# モデルを保存するディレクトリを作成
mkdir -p ~/unsloth/models
```

### 2. Phi-4 Reasoning Plus 8bitモデルのダウンロード

```bash
# Phi-4 Reasoning Plusモデルをダウンロード
curl -L https://huggingface.co/microsoft/Phi-4-Reasoning-Plus-8bit/resolve/main/phi-4-reasoning-plus-8bit.gguf -o ~/unsloth/models/phi-4-reasoning-plus/phi-4-reasoning-plus-8bit.gguf
```

### 3. Qwen 32Bモデルのダウンロード

```bash
# Qwen 32Bモデルをダウンロード
curl -L https://huggingface.co/Qwen/Qwen2-32B-Instruct-GGUF/resolve/main/qwen2-32b-instruct-q4_k_m.gguf -o ~/unsloth/models/qwen32b/qwen2-32b-instruct-q4_k_m.gguf
```

### 4. Unsloth Llama4モデルのセットアップ（既にOllamaでダウンロード済みの場合）

```bash
# Ollamaのモデルディレクトリからシンボリックリンクを作成
ln -s ~/.ollama/models/unsloth/Llama-4-Scout-17B-16E-Instruct-GGUF/q4_k_xl.gguf ~/unsloth/models/ud-q4_k_xl/ud-q4_k_xl.gguf
ln -s ~/.ollama/models/unsloth/Llama-4-Scout-17B-16E-Instruct-GGUF/q2_k_xl.gguf ~/unsloth/models/ud-q2_k_xl/ud-q2_k_xl.gguf
```

## llama.cppの使用方法

### コマンドラインからの実行

```bash
# Phi-4 Reasoning Plusモデルを実行
llama-cli -m ~/unsloth/models/phi-4-reasoning-plus/phi-4-reasoning-plus-8bit.gguf -p "この患者の症状について教えてください" --n-gpu-layers 99

# Qwen 32Bモデルを実行
llama-cli -m ~/unsloth/models/qwen32b/qwen2-32b-instruct-q4_k_m.gguf -p "この患者の症状について教えてください" --n-gpu-layers 99

# Unsloth Llama4 Scoutモデルを実行
llama-cli -m ~/unsloth/models/ud-q4_k_xl/ud-q4_k_xl.gguf -p "この患者の症状について教えてください" --n-gpu-layers 99
```

### サーバーモードでの実行

```bash
# サーバーモードでPhi-4 Reasoning Plusモデルを実行
llama-server -m ~/unsloth/models/phi-4-reasoning-plus/phi-4-reasoning-plus-8bit.gguf --n-gpu-layers 99 --host 0.0.0.0 --port 8080
```

## アプリケーションでの使用方法

Disease Support Finderアプリケーションでは、以下の手順でllama.cppモデルを使用できます：

1. バックエンドサーバーを起動します：
```bash
cd backend/disease-support-backend
poetry run uvicorn app.main_llm_enhanced:app --reload --host 0.0.0.0 --port 8001
```

2. フロントエンドを起動します：
```bash
cd frontend
npm run dev
```

3. ブラウザで `http://localhost:5173` にアクセスします

4. LLMプロバイダー設定パネルで：
   - プロバイダーとして「llama.cpp」を選択
   - モデルとして「phi-4-reasoning-plus-8bit」または「qwen32b」を選択
   - API URLとして「http://localhost:8080」を設定（サーバーモードで実行している場合）
   - または、API URLを空にしてCLIモードで実行（サーバーモードが不要な場合）

## パフォーマンスの最適化

MacBook M4 Maxでのパフォーマンスを最適化するためのヒント：

1. **GPU層の最適化**: `--n-gpu-layers`パラメータを調整して、GPUメモリ使用量とパフォーマンスのバランスを取ります
   - 大きな値（例：99）は可能な限り多くの層をGPUで実行します
   - 小さな値はGPUメモリ使用量を減らしますが、パフォーマンスも低下します

2. **コンテキストサイズの調整**: `--ctx-size`パラメータを調整して、メモリ使用量と長いコンテキストのサポートのバランスを取ります
   - 大きな値（例：8192）は長いコンテキストをサポートしますが、メモリ使用量が増加します
   - 小さな値はメモリ使用量を減らしますが、長いコンテキストをサポートできなくなります

3. **バッチサイズの調整**: `--batch-size`パラメータを調整して、スループットとレイテンシのバランスを取ります
   - 大きな値はスループットを向上させますが、レイテンシが増加します
   - 小さな値はレイテンシを減らしますが、スループットも低下します

## トラブルシューティング

1. **メモリエラーが発生する場合**:
   - `--n-gpu-layers`の値を小さくしてGPUメモリ使用量を減らします
   - `--ctx-size`の値を小さくしてメモリ使用量を減らします
   - より小さなモデル（例：Phi-4 Reasoning Plus）を使用します

2. **Metal GPUアクセラレーションが機能しない場合**:
   - llama.cppが正しくビルドされていることを確認します（`LLAMA_METAL=1 make`）
   - 最新のmacOSバージョンを使用していることを確認します
   - 最新のllama.cppバージョンを使用していることを確認します

3. **モデルのロードに失敗する場合**:
   - モデルファイルが正しくダウンロードされていることを確認します
   - モデルパスが正しいことを確認します
   - モデルファイルの権限が正しいことを確認します

## 参考リンク

- [llama.cpp GitHub リポジトリ](https://github.com/ggerganov/llama.cpp)
- [Phi-4 Reasoning Plus モデル](https://huggingface.co/microsoft/Phi-4-Reasoning-Plus-8bit)
- [Qwen 32B モデル](https://huggingface.co/Qwen/Qwen2-32B-Instruct-GGUF)
