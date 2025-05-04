# LLM検索機能の統合と日本語対応の強化

このPRでは、以下の機能強化と修正を行います：

1. **LLM検索の全検索機能への統合**
   - StatsDisplay コンポーネントに LLM 検索機能を追加
   - LLMProviderSelector を統合して LM Studio と Qwen モデルをデフォルトに設定
   - 検索ステータスと進捗状況の表示機能を追加

2. **LM Studio セットアップガイドの作成**
   - Qwen30B-A3B と Qwen32B モデルのダウンロードと設定手順
   - API サーバーの起動と設定方法
   - パフォーマンス最適化のヒント
   - トラブルシューティング情報

3. **日本語対応の強化**
   - 日本語に強い Qwen モデルを優先的に使用するよう設定
   - LLM 検索インターフェースの日本語化
   - エラーメッセージとステータス表示の日本語化

## 技術的詳細

### LLM検索の統合
- StatsDisplay コンポーネントに LLM 検索機能を追加し、通常の検索と LLM 検索を同じ画面で実行可能に
- LLMProviderSelector コンポーネントを統合して、LM Studio と Qwen モデルを簡単に選択できるように
- 検索ステータスと進捗状況をリアルタイムで表示する機能を追加

### LM Studio セットアップガイド
- 詳細なセットアップ手順を記載した `lmstudio_setup_guide.md` を作成
- Qwen30B-A3B と Qwen32B モデルのダウンロードと設定方法を説明
- API サーバーの起動と設定方法、アプリケーションとの連携方法を解説
- トラブルシューティング情報とパフォーマンス最適化のヒントを提供

## 要求元

Eisuke Dohi (domy1980@gmail.com)

## Devin実行リンク

https://app.devin.ai/sessions/a9d4681d7e214b8aba363d9a138b0b9d
