import React from 'react';

export const LLMInfoPanel: React.FC = () => {
  return (
    <div className="w-full space-y-6 border rounded-lg p-6 bg-white shadow-sm">
      <div>
        <h2 className="text-xl font-bold">ローカルLLM拡張機能について</h2>
        <p className="text-muted-foreground">
          MacBook Pro M4 Max 128GBで実行するローカルLLMを使用した患者会データ収集の精度向上
        </p>
      </div>

      <div className="space-y-4">
        <div>
          <h3 className="text-lg font-semibold">主な機能</h3>
          <ul className="list-disc pl-5 space-y-1 mt-2">
            <li>ウェブサイトコンテンツの高度な分析</li>
            <li>団体タイプの正確な分類（患者会、家族会、支援団体）</li>
            <li>組織の詳細情報の抽出（連絡先、サービス内容など）</li>
            <li>疾患特異性の評価</li>
            <li>検索結果の信頼度スコアリング</li>
          </ul>
        </div>

        <div>
          <h3 className="text-lg font-semibold">カテゴリーフィルタリング</h3>
          <p className="mt-2">
            以下のカテゴリー名は検索対象から除外されます：
          </p>
          <ul className="list-disc pl-5 space-y-1 mt-1 text-sm">
            <li>代謝系疾患</li>
            <li>神経・筋疾患</li>
            <li>循環器系疾患</li>
            <li>免疫系疾患</li>
            <li>皮膚・結合組織疾患</li>
            <li>血液系疾患</li>
            <li>腎・泌尿器系疾患</li>
            <li>呼吸器系疾患</li>
            <li>骨・関節系疾患</li>
            <li>内分泌系疾患</li>
            <li>視覚系疾患</li>
            <li>聴覚・平衡機能系疾患</li>
            <li>筋萎縮性側索硬化症</li>
            <li>球脊髄性筋萎縮症</li>
            <li>消化器系疾患</li>
            <li>耳鼻科系疾患</li>
          </ul>
          <p className="mt-2">
            以下の一般的な用語は検索対象に含まれます：
          </p>
          <ul className="list-disc pl-5 space-y-1 mt-1 text-sm">
            <li>染色体または遺伝子に変化を伴う症候群</li>
            <li>遺伝検査用疾患群</li>
            <li>難病</li>
            <li>指定難病</li>
          </ul>
        </div>

        <div>
          <h3 className="text-lg font-semibold">セットアップ方法</h3>
          <p className="mt-2">
            MacBook Pro M4 Max 128GBでローカルLLMを実行するためのセットアップ手順は、
            リポジトリの <code>mac_setup_guide.md</code> ファイルに記載されています。
          </p>
          <p className="mt-2">
            主な手順:
          </p>
          <ol className="list-decimal pl-5 space-y-1 mt-1">
            <li>Ollamaのインストール</li>
            <li>LLMモデルのダウンロード</li>
            <li>アプリケーションのセットアップ</li>
            <li>LLM拡張バックエンドの起動</li>
          </ol>
        </div>

        <div>
          <h3 className="text-lg font-semibold">推奨モデル</h3>
          <ul className="list-disc pl-5 space-y-1 mt-2">
            <li><strong>Mistral</strong>: バランスの取れた性能と速度（デフォルト）</li>
            <li><strong>Llama 3 (70B)</strong>: 最高の精度（M4 Max 128GBで実行可能）</li>
            <li><strong>TinyLlama</strong>: 軽量で高速（精度は低下）</li>
          </ul>
        </div>

        <div>
          <h3 className="text-lg font-semibold">パフォーマンス最適化</h3>
          <p className="mt-2">
            M4 Maxの128GBメモリを最大限に活用するために:
          </p>
          <ul className="list-disc pl-5 space-y-1 mt-1">
            <li>より大きなモデル（llama3:70b）を使用</li>
            <li>並列処理数を増やす（max_concurrent=8）</li>
            <li>コンテンツキャッシュを高速なSSDに配置</li>
          </ul>
        </div>
      </div>
    </div>
  );
};
