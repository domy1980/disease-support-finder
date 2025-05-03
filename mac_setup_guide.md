# LLM-Enhanced Disease Support Finder - Mac Setup Guide

このガイドでは、MacBook Pro M4 Max 128GBで、ローカルLLMを使用して患者会データ収集の精度を向上させるシステムのセットアップ方法を説明します。

## 必要条件

- MacBook Pro M4 Max 128GB
- macOS Sonoma 14.0以上
- Homebrewがインストールされていること
- Python 3.10以上がインストールされていること

## 1. LLMプロバイダーの選択

このアプリケーションは、以下の2つのLLMプロバイダーをサポートしています：

1. **Ollama** - 軽量で使いやすいローカルLLMフレームワーク
2. **LM Studio** - 高性能なモデル（Qwen30B-A3Bなど）をサポートするGUIベースのLLMフレームワーク

どちらか一方、または両方をインストールして使用できます。

## 2. Ollamaのインストール（オプション）

Ollamaは、ローカルLLMを簡単に実行するためのツールです。

```bash
# Homebrewを使用してOllamaをインストール
brew install ollama

# Ollamaを起動
ollama serve
```

### Ollamaモデルのダウンロード

新しいターミナルウィンドウを開き、以下のコマンドを実行してモデルをダウンロードします。

```bash
# Mistralモデルをダウンロード（推奨）
ollama pull mistral:latest

# または、より小さいモデル
ollama pull llama2:7b

# または、より大きく高性能なモデル（M4 Maxの128GBメモリなら十分実行可能）
ollama pull llama3:70b
```

## 3. LM Studioのインストール（オプション）

LM Studioは、高性能なモデル（Qwen30B-A3Bなど）を実行するためのGUIベースのツールです。

1. [LM Studioの公式サイト](https://lmstudio.ai/)からMac用インストーラーをダウンロード
2. ダウンロードしたDMGファイルを開き、アプリケーションフォルダにドラッグ＆ドロップ
3. LM Studioを起動

### LM Studioモデルのダウンロード

1. LM Studioを起動
2. 「Browse Models」タブをクリック
3. 検索ボックスに「Qwen30B-A3B」と入力
4. モデルを見つけてダウンロードボタンをクリック
5. ダウンロードが完了したら、「Local Models」タブでモデルを選択
6. 「Chat」タブをクリック
7. 右上の「API」ボタンをクリックしてAPIサーバーを起動
8. デフォルトのAPIエンドポイントは `http://localhost:1234/v1` です

## 4. アプリケーションのクローン

```bash
# リポジトリをクローン
git clone https://github.com/domy1980/disease-support-finder.git
cd disease-support-finder
```

## 5. バックエンドのセットアップ

```bash
# バックエンドディレクトリに移動
cd backend/disease-support-backend

# 仮想環境を作成
python -m venv venv
source venv/bin/activate

# 依存関係をインストール
pip install -r requirements.txt

# LLM機能用の追加依存関係をインストール
pip install aiohttp beautifulsoup4
```

## 6. LLM拡張バックエンドの起動

```bash
# マルチプロバイダー対応LLM拡張バックエンドを起動
uvicorn app.main_llm_enhanced:app --reload --host 0.0.0.0 --port 8001
```

## 7. フロントエンドのセットアップ

新しいターミナルウィンドウを開き、以下のコマンドを実行します。

```bash
# フロントエンドディレクトリに移動
cd frontend

# 依存関係をインストール
npm install

# 開発サーバーを起動
npm run dev
```

## 8. LLM拡張機能の使用方法

1. ブラウザで `http://localhost:5173` にアクセス
2. 「LLM検索」タブに移動
3. LLMプロバイダーとモデルを選択
   - Ollama: mistral:latest（デフォルト）
   - LM Studio: Qwen30B-A3B（推奨）
4. 「LLM拡張検索を実行」ボタンをクリックして、LLM拡張検索を開始

## 9. カテゴリーフィルタリング

システムは以下のカテゴリー名を検索対象から除外します：

- 代謝系疾患
- 神経・筋疾患
- 循環器系疾患
- 免疫系疾患
- 皮膚・結合組織疾患
- 血液系疾患
- 腎・泌尿器系疾患
- 呼吸器系疾患
- 骨・関節系疾患
- 内分泌系疾患
- 視覚系疾患
- 聴覚・平衡機能系疾患
- 筋萎縮性側索硬化症
- 球脊髄性筋萎縮症
- 消化器系疾患
- 耳鼻科系疾患

以下の一般的な用語は検索対象に含まれます：

- 染色体または遺伝子に変化を伴う症候群
- 遺伝検査用疾患群
- 難病
- 指定難病

## 10. 高度な設定

### 異なるモデルの使用

フロントエンドのLLMプロバイダー設定から、使用するプロバイダーとモデルを選択できます。

### キャッシュディレクトリの変更

ウェブコンテンツのキャッシュディレクトリを変更するには、`app/llm_web_scraper_enhanced.py`ファイルの`cache_dir`パラメータを編集します。

### 並列処理の調整

M4 Maxの高性能を活かすために、`app/llm_stats_manager_enhanced.py`ファイルの`daily_search_task`メソッドの`max_concurrent`パラメータを調整できます。デフォルトは3ですが、5〜8に増やすことで処理速度が向上します。

## トラブルシューティング

### Ollamaが起動しない場合

```bash
# Ollamaのステータスを確認
ps aux | grep ollama

# 必要に応じて再起動
killall ollama
ollama serve
```

### LM Studioが起動しない場合

1. LM Studioアプリケーションを再起動
2. APIサーバーが起動していることを確認（右上の「API」ボタンが緑色になっている）
3. デフォルトのAPIエンドポイント `http://localhost:1234/v1` が正しく設定されていることを確認

### メモリ使用量が高い場合

より小さいモデルを使用するか、`max_concurrent`パラメータを小さくしてください。

```bash
# Ollamaでより小さいモデルを使用
ollama pull tinyllama:latest

# または、LM Studioで小さいモデルを選択
# 例: Phi-3-mini-4k-instruct
```

### ウェブスクレイピングがブロックされる場合

`app/llm_web_scraper_enhanced.py`ファイルの`headers`を編集して、より本物のブラウザのように見せることができます。

## パフォーマンス最適化

M4 Maxの128GBメモリを最大限に活用するために、以下の設定を検討してください：

1. LM StudioでQwen30B-A3Bモデルを使用する（最高の精度）
2. 並列処理数を増やす（max_concurrent=8）
3. コンテンツキャッシュを高速なSSDに配置する

これらの設定により、データ収集の精度と速度が大幅に向上します。

## LLMプロバイダーの比較

| 機能 | Ollama | LM Studio |
|------|--------|-----------|
| 使いやすさ | ★★★★★ | ★★★★☆ |
| モデルの多様性 | ★★★☆☆ | ★★★★★ |
| 精度 | ★★★☆☆ | ★★★★★ |
| メモリ効率 | ★★★★☆ | ★★★☆☆ |
| 処理速度 | ★★★★☆ | ★★★☆☆ |
| セットアップの容易さ | ★★★★★ | ★★★★☆ |

Qwen30B-A3Bモデルは、日本語の理解力が特に高く、患者会や支援団体の分類に優れています。
