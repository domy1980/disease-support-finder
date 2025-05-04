# LLM検索API修正とローカル開発環境の設定

このPRでは、LLM検索機能のAPIエラーを修正し、ローカル開発環境でLLM機能をテストできるようにするための変更を行いました。

## 変更内容

1. **フロントエンドの.envファイルを更新**
   - APIのURLをローカル開発環境（`http://localhost:8000`）に変更
   - これにより、ローカル環境でLLM機能をテストできるようになります

2. **ローカルバックエンド実行スクリプトの追加**
   - `run_local_backend.sh`スクリプトを追加
   - LLMエンドポイントを含む拡張バックエンドを実行するためのスクリプト
   - 必要なディレクトリの作成と依存関係のインストールを自動化

3. **システムアーキテクチャ図の改善**
   - 検索フローとデータ処理パイプラインの詳細な説明を追加
   - LLM検証プロセスの図解を改善

## 問題の解決方法

現在デプロイされているバックエンド（https://app-mhqkgfhg.fly.dev）にはLLM関連のAPIエンドポイントが実装されていないため、LLM検索機能でエラーが発生していました。この問題を解決するために、ローカル環境でLLMエンドポイントを含むバックエンドを実行できるようにしました。

## 使用方法

1. **ローカルバックエンドの起動**
   ```bash
   chmod +x run_local_backend.sh
   ./run_local_backend.sh
   ```

2. **フロントエンドの起動**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **LLM検索機能のテスト**
   - ブラウザで`http://localhost:5173`にアクセス
   - LLM検索機能を使用して、正常に動作することを確認

## 注意事項

- ローカル環境でLLM機能をテストするには、Ollama、LM Studio、またはllama.cppなどのLLMプロバイダーが必要です
- 詳細な設定方法は各プロバイダーのセットアップガイドを参照してください

## 関連リンク

- [Devinセッション](https://app.devin.ai/sessions/a9d4681d7e214b8aba363d9a138b0b9d)
- [システムアーキテクチャ図](./system_architecture_diagram.md)
- [検索戦略ドキュメント](./search_strategy_documentation.md)
