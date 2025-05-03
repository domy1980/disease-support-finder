# MLX サポートの追加と4ビット量子化モデルの対応

このPRでは、Apple Silicon向けに最適化されたMLXフレームワークのサポートを追加し、Qwenモデルを高速に実行できるようにします。また、Llama4 ScoutとLlama4 Maverickの4ビット量子化モデルのサポートも強化します。

## 主な変更点

- **MLXプロバイダーの実装**: Apple Silicon向けに最適化されたMLXフレームワークをサポート
- **Qwenモデルの対応**: Qwen 1.5シリーズ（0.5B〜14B）の4ビット量子化モデルをサポート
- **プロバイダー抽象化レイヤーの拡張**: OllamaとMLXの両方をサポートする統一インターフェース
- **フロントエンド拡張**: プロバイダーとモデルを選択できるUIコンポーネントの更新
- **ドキュメント更新**: MLXのセットアップと使用方法に関するガイドの追加

## 技術的な詳細

- 新しいプロバイダー実装: `MLXProvider`
- サポートされるモデル: Qwen 1.5シリーズ（4ビット量子化）、Llama 3（4ビット量子化）
- 実行方法: HTTP APIサーバーまたは直接Pythonから実行
- フロントエンド対応: MLXプロバイダーの選択と設定UIの追加

## テスト済み機能

- MLXプロバイダーの動作確認
- 4ビット量子化Qwenモデルの実行
- プロバイダー切り替え機能
- モデル選択機能

## 使用方法

### MLX + Qwenモデル

```bash
# MLXとmlx-lmをインストール
pip install mlx mlx-lm

# Qwen 4B（バランスの取れたモデル）
git clone https://huggingface.co/mlx-community/Qwen1.5-4B-Chat-4bit ~/mlx-models/Qwen/Qwen1.5-4B-Chat-4bit

# モデルを直接実行
python -m mlx_lm.generate --model ~/mlx-models/Qwen/Qwen1.5-4B-Chat-4bit --prompt "こんにちは"
```

詳細なセットアップ手順は `mac_setup_guide_updated.md` を参照してください。

## 要求元

Eisuke Dohi (domy1980@gmail.com)

## Devin実行リンク

https://app.devin.ai/sessions/a9d4681d7e214b8aba363d9a138b0b9d
