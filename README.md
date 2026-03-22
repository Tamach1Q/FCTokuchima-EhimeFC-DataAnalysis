# FC Tokushima / Ehime FC Data Analysis

FC徳島・愛媛FC向けのサッカーデータ分析リポジトリです。  
Football Box と SkillCorner の選手データを統合し、前線選手の特徴をクラスタリングで分類したうえで、RandomForest により各クラスターを特徴づける変数を確認します。

## 概要

このリポジトリでは、主に以下の流れで分析を行っています。

1. Football Box と SkillCorner の生データを収集
2. 選手名マッピングを用いてデータを統合
3. 90分換算などの前処理を実施
4. 9変数で K-Means クラスタリングを実行
5. RandomForest で各クラスターの判別に重要な変数を確認
6. クラスター比較用の CSV を出力

現在の成果物では、分析対象は `295名`、クラスター数は `4` です。

## 使用変数

クラスタリングと RandomForest では、以下の 9 変数を使用しています。

- `PA内シュート_per90`
- `PA内シュート決定率(%)`
- `Explosive Acceleration to Sprint Count TIP_per90`
- `ボールゲイン_per90`
- `Sprint Count OTIP_per90`
- `M/min OTIP`
- `空中戦勝率(%)`
- `パス_per90`
- `PSV-99`

## クラスターの解釈

`RandomForestの結果.txt` をもとに、4クラスターは暫定的に次のように解釈しています。

- `Cluster 0`: バランス型
- `Cluster 1`: 守備型
- `Cluster 2`: 起点型
- `Cluster 3`: 得点型

コード上では `0〜3` の数値ラベルを使っており、上記名称は分析メモとしての解釈です。

## 主なファイル

- `merge_files.py`: Football Box と SkillCorner のデータ統合、選手単位集計、`clustering_base_data.csv` 作成
- `clustering_base_data.py`: 生データ読み込み確認用スクリプト
- `kmeans_clustering.py`: 9変数で K-Means を実行し、`kmeans_results_refined.csv` を出力
- `randomforest.py`: 各クラスターの重要変数と代表選手を確認
- `make_cluster_comparison_csv.py`: クラスターごとの平均比較 CSV を出力
- `RandomForestの結果.txt`: クラスター解釈メモ

## 出力ファイル

- `clustering_base_data.csv`
  - 統合・集計済みの分析ベースデータ
  - 現在は `295行 × 88列`
- `kmeans_results_refined.csv`
  - クラスタリング結果付きデータ
  - `Cluster_Refined` 列を追加
- `cluster_comparison_refined.csv`
  - 9変数についてクラスター平均、全体平均との差、順位、人数を一覧化した比較表

クラスター人数は以下の通りです。

- `Cluster 0`: 92名
- `Cluster 1`: 58名
- `Cluster 2`: 75名
- `Cluster 3`: 70名

## ディレクトリ構成

```text
.
├── README.md
├── merge_files.py
├── clustering_base_data.py
├── kmeans_clustering.py
├── randomforest.py
├── make_cluster_comparison_csv.py
├── clustering_base_data.csv
├── kmeans_results_refined.csv
├── cluster_comparison_refined.csv
├── RandomForestの結果.txt
├── csv/
│   ├── fb_unique_players.csv
│   ├── sc_unique_players.csv
│   ├── cf_name_mapping_fixed.csv
│   └── master_name_mapping_final.csv
└── 生データ -> 外部ストレージ上の元データ
```

## 実行環境

想定ライブラリ:

- `pandas`
- `numpy`
- `scikit-learn`
- `openpyxl`

例:

```bash
pip install pandas numpy scikit-learn openpyxl
```

## 実行手順

### 1. ベースデータの作成

```bash
python merge_files.py
```

### 2. クラスタリング

```bash
python kmeans_clustering.py
```

### 3. クラスター解釈の確認

```bash
python randomforest.py
```

### 4. 比較用 CSV の出力

```bash
python make_cluster_comparison_csv.py
```

## 注意点

- `merge_files.py` と `clustering_base_data.py` では、生データの参照先がローカル環境の絶対パスになっています。
- 名前マッピング CSV は `csv/master_name_mapping_final.csv` にありますが、スクリプト側の参照パスは環境に応じて調整が必要です。
- `生データ` は外部ストレージへのリンクを前提にしています。GitHub 上ではそのまま再現できないため、利用時は各自の環境に合わせてパスを設定してください。

## 今後の改善候補

- `requirements.txt` または `pyproject.toml` の追加
- データパスの相対化
- Notebook 化による可視化追加
- クラスター解釈の図表化
