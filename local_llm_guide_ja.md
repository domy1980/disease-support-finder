# ローカルLLM設定・運用ガイド

このガイドでは、難病・希少疾患支援団体検索アプリケーションで使用できるローカルLLMの設定方法と運用方法について詳しく説明します。

## 目次

1. [サポートされているLLMプロバイダー](#サポートされているllmプロバイダー)
2. [Ollamaの設定と運用](#ollamaの設定と運用)
3. [MLXの設定と運用](#mlxの設定と運用)
4. [LM Studioの設定と運用](#lm-studioの設定と運用)
5. [llama.cppの設定と運用](#llamacppの設定と運用)
6. [Unsloth Llama4の設定と運用](#unsloth-llama4の設定と運用)
7. [トラブルシューティング](#トラブルシューティング)
8. [パフォーマンス最適化](#パフォーマンス最適化)

## サポートされているLLMプロバイダー

本アプリケーションでは、以下のLLMプロバイダーをサポートしています：

| プロバイダー | 特徴 | 推奨モデル | 必要メモリ |
|------------|------|-----------|----------|
| Ollama | 簡単なセットアップ、多様なモデル | Mistral, Llama 3 | 16GB+ |
| MLX | Apple Silicon最適化、高速 | Qwen30B-A3B | 32GB+ |
| LM Studio | GUIインターフェース、使いやすさ | Qwen32B, Phi-4 | 32GB+ |
| llama.cpp | Metal GPU加速、高性能 | Phi-4, Qwen32B | 64GB+ |
| Unsloth | Llama4モデル専用 | Llama-4-Scout-17B | 32GB+ |

## Ollamaの設定と運用

### インストール

```bash
# Homebrewを使用してインストール
brew install ollama

# または公式サイトからダウンロード
# https://ollama.com/download
```

### モデルのダウンロード

```bash
# Mistralモデル（推奨）
ollama pull mistral:latest

# Llama 3モデル（70B、高性能）
ollama pull llama3:70b-q4_0

# Unsloth Llama4モデル
ollama run hf.co/unsloth/Llama-4-Scout-17B-16E-Instruct-GGUF:Q4_K_XL
ollama run hf.co/unsloth/Llama-4-Scout-17B-16E-Instruct-GGUF:Q2_K_XL
```

### Ollamaサーバーの起動

```bash
# デフォルトポート（11434）で起動
ollama serve
```

### アプリケーションでの使用方法

1. バックエンドサーバーを起動
2. フロントエンドを起動
3. LLMプロバイダー設定パネルで「Ollama」を選択
4. モデルとして「mistral:latest」または「llama3:70b-q4_0」を選択
5. API URLとして「http://localhost:11434」を設定

## MLXの設定と運用

### インストール

```bash
# Homebrewを使用してインストール
brew install mlx

# Pythonパッケージのインストール
pip install mlx mlx-lm
```

### モデルのダウンロード

```bash
# Qwen30B-A3Bモデルをダウンロード
git clone https://github.com/mlx-community/mlx-community-models.git
cd mlx-community-models
python -m mlx_lm.download --model mlx-community/Qwen-30B-A3B-4bit
```

### MLXサーバーの起動

```bash
# モデルを指定してサーバーを起動
python -m mlx_lm.server --model mlx-community/Qwen-30B-A3B-4bit --host 0.0.0.0 --port 8080
```

### アプリケーションでの使用方法

1. バックエンドサーバーを起動
2. フロントエンドを起動
3. LLMプロバイダー設定パネルで「MLX」を選択
4. モデルとして「mlx-community/Qwen-30B-A3B-4bit」を選択
5. API URLとして「http://localhost:8080」を設定

## LM Studioの設定と運用

### インストール

1. [LM Studio公式サイト](https://lmstudio.ai/)からMac版をダウンロード
2. アプリケーションをインストール

### モデルのダウンロード

1. LM Studioを起動
2. 「Browse Models」タブを選択
3. 検索バーで「Qwen32B」または「Phi-4」を検索
4. モデルをダウンロード

### LM Studioサーバーの起動

1. ダウンロードしたモデルを選択
2. 「Local Server」タブを選択
3. 「Start Server」ボタンをクリック

### アプリケーションでの使用方法

1. バックエンドサーバーを起動
2. フロントエンドを起動
3. LLMプロバイダー設定パネルで「LM Studio」を選択
4. モデルとして使用中のモデル名を選択
5. API URLとして「http://localhost:1234/v1」を設定

## llama.cppの設定と運用

### インストール

```bash
# Homebrewを使用してインストール
brew install llama.cpp

# または、ソースからビルド
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp
LLAMA_METAL=1 make
```

### モデルのダウンロード

```bash
# モデルディレクトリの作成
mkdir -p ~/unsloth/models

# Phi-4 Reasoning Plusモデルのダウンロード
curl -L https://huggingface.co/microsoft/Phi-4-Reasoning-Plus-8bit/resolve/main/phi-4-reasoning-plus-8bit.gguf -o ~/unsloth/models/phi-4-reasoning-plus/phi-4-reasoning-plus-8bit.gguf

# Qwen 32Bモデルのダウンロード
curl -L https://huggingface.co/Qwen/Qwen2-32B-Instruct-GGUF/resolve/main/qwen2-32b-instruct-q4_k_m.gguf -o ~/unsloth/models/qwen32b/qwen2-32b-instruct-q4_k_m.gguf
```

### llama.cppサーバーの起動

```bash
# サーバーモードでPhi-4 Reasoning Plusモデルを実行
llama-server -m ~/unsloth/models/phi-4-reasoning-plus/phi-4-reasoning-plus-8bit.gguf --n-gpu-layers 99 --host 0.0.0.0 --port 8080
```

### アプリケーションでの使用方法

1. バックエンドサーバーを起動
2. フロントエンドを起動
3. LLMプロバイダー設定パネルで「llama.cpp」を選択
4. モデルとして「phi-4-reasoning-plus-8bit」または「qwen32b」を選択
5. API URLとして「http://localhost:8080」を設定

## Unsloth Llama4の設定と運用

### Ollamaを使用したセットアップ

```bash
# Unsloth Llama4モデルをダウンロード
ollama run hf.co/unsloth/Llama-4-Scout-17B-16E-Instruct-GGUF:Q4_K_XL
ollama run hf.co/unsloth/Llama-4-Scout-17B-16E-Instruct-GGUF:Q2_K_XL
```

### アプリケーションでの使用方法

1. バックエンドサーバーを起動
2. フロントエンドを起動
3. LLMプロバイダー設定パネルで「Ollama」を選択
4. モデルとして「unsloth/Llama-4-Scout-17B-16E-Instruct-GGUF:Q4_K_XL」または「unsloth/Llama-4-Scout-17B-16E-Instruct-GGUF:Q2_K_XL」を選択
5. API URLとして「http://localhost:11434」を設定

## トラブルシューティング

### 一般的な問題

| 問題 | 解決策 |
|-----|-------|
| メモリ不足エラー | モデルサイズを小さくする（Q4_K→Q2_K）、または--n-gpu-layersを減らす |
| 応答が遅い | バッチサイズを調整、コンテキストサイズを小さくする |
| モデルが見つからない | モデル名を正確に指定、パスが正しいか確認 |
| APIエラー | ポート番号とホスト設定を確認、ファイアウォール設定を確認 |

### Ollama特有の問題

- **エラー**: `pull model manifest: file does not exist`
  - **解決策**: モデル名を正確に指定、または別のモデルを試す

- **エラー**: `failed to load model: no such file or directory`
  - **解決策**: Ollamaを再起動、モデルを再ダウンロード

### MLX特有の問題

- **エラー**: `ImportError: No module named 'mlx'`
  - **解決策**: `pip install mlx mlx-lm`を実行

- **エラー**: `Failed to load model: ...`
  - **解決策**: モデルパスを確認、再ダウンロード

### llama.cpp特有の問題

- **エラー**: `Metal: Not enough memory`
  - **解決策**: `--n-gpu-layers`の値を小さくする（例：99→32）

- **エラー**: `ggml_metal_add_buffer: failed to create buffer`
  - **解決策**: システムを再起動、他のGPUを使用するアプリを閉じる

## パフォーマンス最適化

### MacBook M4 Max向け最適化

1. **GPU層の最適化**:
   - `--n-gpu-layers`パラメータを調整（大きな値→GPUで多くの層を実行、小さな値→GPUメモリ使用量減少）

2. **コンテキストサイズの調整**:
   - `--ctx-size`パラメータを調整（大きな値→長いコンテキスト、小さな値→メモリ使用量減少）

3. **バッチサイズの調整**:
   - `--batch-size`パラメータを調整（大きな値→スループット向上、小さな値→レイテンシ減少）

4. **量子化レベルの選択**:
   - Q4_K: バランスの取れた精度とパフォーマンス
   - Q2_K: 最高速だが精度は低下

### モデル別推奨設定

| モデル | 推奨設定 | メモリ要件 |
|-------|---------|----------|
| Mistral | デフォルト | 16GB+ |
| Llama 3 (70B) | --n-gpu-layers 64 --ctx-size 4096 | 64GB+ |
| Qwen30B-A3B | --n-gpu-layers 48 --ctx-size 2048 | 32GB+ |
| Phi-4 | --n-gpu-layers 32 --ctx-size 2048 | 32GB+ |
| Qwen32B | --n-gpu-layers 64 --ctx-size 4096 | 64GB+ |
| Llama-4-Scout-17B | Q4_K_XL（バランス）またはQ2_K_XL（高速） | 32GB+ |

## アプリケーションでのLLM設定

アプリケーションのフロントエンドでは、LLMプロバイダー設定パネルから以下の設定が可能です：

1. **プロバイダー選択**:
   - Ollama、MLX、LM Studio、llama.cppから選択

2. **モデル選択**:
   - 選択したプロバイダーで利用可能なモデルから選択

3. **API URL設定**:
   - LLMサーバーのURLを指定（デフォルト値が自動入力されます）

4. **Metal最適化**:
   - Metal対応モデルを選択すると自動的に最適化されます

## 高度な使用方法

### バッチ処理の実行

アプリケーションでは、全疾患に対するバッチ処理を実行できます：

1. 「全疾患LLM検索実行」ボタンをクリック
2. 処理状況はリアルタイムで表示されます
3. 処理は自動的にバックグラウンドで実行され、結果は保存されます

### カスタムプロンプトの設定

上級ユーザー向けに、カスタムプロンプトの設定も可能です：

1. バックエンドの設定ファイルを編集
2. システムプロンプトとユーザープロンプトをカスタマイズ
3. 特定の疾患や団体タイプに特化したプロンプトを作成可能

### データのエクスポート/インポート

収集したデータのエクスポート/インポートも可能です：

1. 「データエクスポート」機能でJSONファイルとして保存
2. 「データインポート」機能で外部データを取り込み
3. データのバックアップや共有に便利

## まとめ

本ガイドでは、難病・希少疾患支援団体検索アプリケーションで使用できる様々なローカルLLMの設定方法と運用方法を説明しました。MacBook M4 Maxの性能を最大限に活用するための最適化方法も紹介しています。

ご質問やフィードバックがありましたら、GitHubリポジトリのIssueセクションにてお知らせください。
