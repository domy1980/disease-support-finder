# モデル設定の修正

このPRでは、以下の修正を行います：

1. **Qwen30B-A3Bモデルの移動**: MLXプロバイダーからLM Studioプロバイダーへ移動
2. **Llama3-70Bのダウンロード名の修正**: `llama3:70b-q4_0` から `llama3:70b` へ修正

## 変更内容

### ドキュメント修正
- `README_ja.md`: MLXプロバイダーの説明からQwen30B-A3Bを削除
- `local_llm_guide_ja.md`: 
  - プロバイダー表からQwen30B-A3Bを削除し、LM Studioに追加
  - MLXセットアップ手順をLlama-3-8Bに更新
  - LM Studioセットアップ手順にQwen30B-A3Bを追加
  - Llama3-70Bのダウンロード名を修正

### コード修正
- `mlx_provider.py`: 推奨モデルリストからQwen30B-A3Bを削除
- `lmstudio_provider.py`: 推奨モデルリストにQwen30B-A3Bを追加

## 要求元

Eisuke Dohi (domy1980@gmail.com)

## Devin実行リンク

https://app.devin.ai/sessions/a9d4681d7e214b8aba363d9a138b0b9d
