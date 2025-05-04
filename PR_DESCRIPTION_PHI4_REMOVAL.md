# 日本語対応の強化とモデル設定の修正

このPRでは、以下の修正と機能強化を行います：

1. **Phi-4モデルの削除**
   - 日本語サポート不足のため、Phi-4モデルを推奨モデルから完全に削除
   - README_ja.mdとlocal_llm_guide_ja.mdから全てのPhi-4関連の記述を削除

2. **Qwen30B-A3BとQwen32Bの強化**
   - LM Studioプロバイダーでの両モデルのサポートを強化
   - 日本語対応を明示的に記載

3. **ドキュメントの更新**
   - `README_ja.md`の更新：Phi-4を削除し、日本語対応モデルを強調
   - `local_llm_guide_ja.md`の更新：Phi-4関連の記述を削除し、Qwen30B-A3Bの設定手順を追加

## 技術的詳細

- Phi-4モデルは日本語や短いコンテキストに対応していないため、推奨モデルから削除
- Qwen30B-A3BとQwen32Bは日本語対応が優れているため、これらに焦点を当てる
- LM Studioプロバイダーの設定を更新し、Qwen30B-A3Bを適切にサポート

## 要求元

Eisuke Dohi (domy1980@gmail.com)

## Devin実行リンク

https://app.devin.ai/sessions/a9d4681d7e214b8aba363d9a138b0b9d
