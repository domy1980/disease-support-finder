# Unsloth Llama4 セットアップガイド for MacBook M4 Max

このガイドでは、MacBook M4 Max上でUnsloth Dynamic v2を使用してLlama4モデルを実行する方法を説明します。Unslothは、LLMの量子化に最適なパフォーマンスを提供する最新の手法です。

## 前提条件

- MacBook M4 Max（128GB RAM推奨）
- [Ollama](https://ollama.ai/)がインストール済み
- ターミナルの基本的な知識

## Unsloth Llama4モデルのインストール

Unslothは、Hugging Faceからモデルを直接Ollamaにプルすることができます。以下のコマンドを使用して、Llama4 Scoutモデルの2つの異なる量子化バージョンをインストールします：

```bash
# 超高速バージョン（Q2量子化）- サイズが小さく、非常に高速
ollama run hf.co/unsloth/Llama-4-Scout-17B-16E-Instruct-GGUF:Q2_K_XL

# 高精度バージョン（Q4量子化）- 精度とパフォーマンスのバランスが良い
ollama run hf.co/unsloth/Llama-4-Scout-17B-16E-Instruct-GGUF:Q4_K_XL
```

これらのコマンドは、モデルをダウンロードして実行します。初回実行時には、モデルのダウンロードに時間がかかる場合があります。

## モデルの特徴

### Llama-4-Scout-17B-16E-Instruct-GGUF:Q2_K_XL
- **サイズ**: 約4.5GB（元の17Bモデルから大幅に削減）
- **速度**: 非常に高速（標準モデルの約4倍）
- **メモリ使用量**: 低（約6-8GB RAM）
- **用途**: 高速な応答が必要な場合や、リソースが限られている場合に最適

### Llama-4-Scout-17B-16E-Instruct-GGUF:Q4_K_XL
- **サイズ**: 約9GB
- **速度**: 高速（標準モデルの約2倍）
- **メモリ使用量**: 中程度（約12-15GB RAM）
- **用途**: 精度と速度のバランスが取れたモデルが必要な場合に最適

## アプリケーションでの使用方法

Disease Support Finderアプリケーションでは、以下の手順でUnsloth Llama4モデルを使用できます：

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
   - プロバイダーとして「Ollama」を選択
   - モデルとして「unsloth/Llama-4-Scout-17B-16E-Instruct-GGUF:Q2_K_XL」または「unsloth/Llama-4-Scout-17B-16E-Instruct-GGUF:Q4_K_XL」を選択
   - API URLとして「http://localhost:11434」を設定

## パフォーマンスの最適化

MacBook M4 Maxでのパフォーマンスを最適化するためのヒント：

1. **メモリ管理**: 他の大きなアプリケーションを閉じて、LLMに十分なメモリを確保します

2. **冷却**: 長時間の推論タスクでは、MacBookが適切に冷却されていることを確認します

3. **バッテリー vs 電源**: 最高のパフォーマンスを得るには、電源に接続した状態で使用することをお勧めします

4. **モデル選択**: リソースに応じて適切なモデルを選択します：
   - 高速な応答が必要な場合は `Q2_K_XL` モデル
   - より高い精度が必要な場合は `Q4_K_XL` モデル

## トラブルシューティング

1. **モデルのダウンロードに失敗する場合**:
   - インターネット接続を確認します
   - Ollamaを再起動します: `killall ollama && ollama serve`
   - 再度ダウンロードを試みます

2. **メモリエラーが発生する場合**:
   - 他のアプリケーションを閉じてメモリを解放します
   - より小さなモデル（Q2_K_XL）を使用します
   - Ollamaの設定で使用するGPUメモリを制限します

3. **応答が遅い場合**:
   - 初回の推論は遅くなる場合があります（モデルがロードされるため）
   - 電源に接続していることを確認します
   - MacBookが過熱していないことを確認します

## 参考リンク

- [Unsloth Dynamic v2 公式ブログ](https://unsloth.ai/blog/dynamic-v2)
- [Hugging Face - Unsloth Llama4 Scout モデル](https://huggingface.co/unsloth/Llama-4-Scout-17B-16E-Instruct-GGUF)
- [Ollama 公式ドキュメント](https://ollama.ai/docs)
