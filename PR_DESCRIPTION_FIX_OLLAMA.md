# Ollama モデル参照の修正

このPRでは、Ollamaで利用できないLlama4モデルの参照を修正し、実際に利用可能なモデルに置き換えます。

## 主な変更点

- **セットアップガイドの更新**: `mac_setup_guide_updated.md`のOllamaモデル参照を修正
- **バックエンドコードの更新**: 利用できないLlama4モデルの参照を削除し、利用可能なモデルに置き換え
- **推奨モデルリストの更新**: 以下の利用可能なモデルを追加
  - Llama3 8B
  - Llama3 70B（4ビット量子化）
  - Mistral（標準版と4ビット量子化版）
  - Gemma 7B（Google製）
  - Phi-3 Mini（Microsoft製）

## 修正の背景

ユーザーからのフィードバックにより、ドキュメントとコードで参照されていたLlama4モデル（`llama4:7b`、`llama4-scout:8b-q4_0`、`llama4-maverick:8b-q4_0`）がOllamaで利用できないことが判明しました。このPRでは、これらの参照を実際に利用可能なモデルに置き換えています。

## 影響範囲

- `mac_setup_guide_updated.md`: セットアップ手順の更新
- `backend/disease-support-backend/app/llm_providers/ollama_provider.py`: 推奨モデルリストの更新
- `backend/disease-support-backend/app/api_llm_enhanced.py`: デフォルトモデルリストの更新

## 要求元

Eisuke Dohi (domy1980@gmail.com)

## Devin実行リンク

https://app.devin.ai/sessions/a9d4681d7e214b8aba363d9a138b0b9d
